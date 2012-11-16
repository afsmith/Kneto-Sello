
import ldap
import pprint

from django.conf import settings
from django.contrib.auth.models import User, Group, SiteProfileNotAvailable
from django.contrib.auth.views import login
from django.core.exceptions import ImproperlyConfigured, ObjectDoesNotExist
from django_auth_ldap.backend import LDAPBackend, _LDAPUser, LDAPSettings, _LDAPUserGroups
from django_auth_ldap.config import LDAPSearch, GroupOfNamesType, PosixGroupType, _LDAPConfig
from django_auth_ldap import config

from management import models
from administration.models import get_entry, ConfigEntry, LDAPGroupConfig



logger = _LDAPConfig.get_logger()


class PlatoLDAPBackend(LDAPBackend):

    def __init__(self):
        super(PlatoLDAPBackend, self).__init__()
        ldap_settings.__init__()


    def authenticate(self, username, password):

        if str(ldap_settings.AUTH_LDAP_IS_USED) == 'False':

            return None

        user = None
        try:
            user = User.objects.get(username=username)
            if not user.get_profile().ldap_user:
                return None
        except ObjectDoesNotExist:
            pass

        ldap_user = PlatoLDAPUser(self, username=username)
        user = ldap_user.authenticate(password)
        return user


    def get_or_create_user(self, username, ldap_user):
        """
        This must return a (User, created) 2-tuple for the given LDAP user.
        username is the Django-friendly username of the user. ldap_user.dn is
        the user's DN and ldap_user.attrs contains all of their LDAP attributes.
        """
        return User.objects.get_or_create(username=username)

    def _populate_required_groups(self):
        for group_dn in ldap_settings.AUTH_LDAP_REQUIRE_GROUPS:
            group, created = Group.objects.get_or_create(name=group_dn.name)

class PlatoLDAPUser(_LDAPUser):
    def __init__(self, backend, username=None, user=None):
        super(PlatoLDAPUser, self).__init__(backend, username=username, user=user)

    def authenticate(self, password):
        """
        Authenticates against the LDAP directory and returns the corresponding
        User object if successful. Returns None on failure.
        """
        user = None

        try:
            self._authenticate_user_dn(password)
            self._check_requirements()
            self._get_or_create_user()
            user = self._user
        except self.AuthenticationFailed, e:
            logger.debug(u"Authentication failed for %s" % self._username)
        except self.ldap.LDAPError, e:
            logger.warning(u"Caught LDAPError while authenticating %s: %s",
                self._username, pprint.pformat(e))
        except Exception, e:
            logger.warning(u"Caught Exception while authenticating %s: %s",
                self._username, pprint.pformat(e))
            raise

        return user

    def _authenticate_user_dn(self, password):
        """
        Binds to the LDAP server with the user's DN and password. Raises
        AuthenticationFailed on failure.
        """
        try:
            self._bind_as(self.dn, password)
        except self.ldap.INVALID_CREDENTIALS, e:
            raise self.AuthenticationFailed("User DN/password rejected by LDAP server.")

    def _bind_as(self, bind_dn, bind_password):
        """
        Binds to the LDAP server with the given credentials. This does not trap
        exceptions.
        """
        self._get_connection().simple_bind_s(bind_dn.encode('utf-8'),
            bind_password.encode('utf-8'))
        self._connection_bound = True

    def _get_connection(self):
        """
        Returns our cached LDAPObject, which may or may not be bound.
        """
        if self._connection is None:
            self._connection = self.ldap.initialize(ldap_settings.AUTH_LDAP_SERVER_URI)

            for opt, value in ldap_settings.AUTH_LDAP_CONNECTION_OPTIONS.iteritems():
                self._connection.set_option(opt, value)

            if ldap_settings.AUTH_LDAP_START_TLS:
                logger.debug("Initiating TLS")
                self._connection.start_tls_s()

        return self._connection

    def _load_user_dn(self):
        """
        Returns the (cached) distinguished name of our user. This will
        ultimately either construct the DN from a template in
        AUTH_LDAP_USER_DN_TEMPLATE or connect to the server and search for it.
        This may result in an AuthenticationFailed exception if we do not get
        satisfactory results searching for the user's DN.
        """
        if self._using_simple_bind_mode():
            self._construct_simple_user_dn()
        else:
            self._search_for_user_dn()

    def _search_for_user_dn(self):
        """
        Searches the directory for a user matching AUTH_LDAP_USER_SEARCH.
        Populates self._user_dn and self._user_attrs.
        """
        search = ldap_settings.AUTH_LDAP_USER_SEARCH
        if search is None:
            raise ImproperlyConfigured('AUTH_LDAP_USER_SEARCH must be an LDAPSearch instance.')

        results = search.execute(self.connection, {'discriminant': ldap_settings.AUTH_LDAP_USER_DISCRIMINANT,
                                                    'user': self._username})
        if results is None or len(results) != 1:
            raise self.AuthenticationFailed("AUTH_LDAP_USER_SEARCH failed to return exactly one result.")

        (self._user_dn, self._user_attrs) = results[0]

    def _using_simple_bind_mode(self):
        return (ldap_settings.AUTH_LDAP_USER_DN_TEMPLATE is not None)

    def _construct_simple_user_dn(self):
        template = ldap_settings.AUTH_LDAP_USER_DN_TEMPLATE
        username = self.ldap.dn.escape_dn_chars(self._username)

        self._user_dn = template % {'user': username}

    def _populate_user(self):
        super(PlatoLDAPUser, self)._populate_user()

    def _populate_user_from_attributes(self):
        for field, value in ldap_settings.AUTH_LDAP_USER_ATTR_MAP.items():
            try:
                setattr(self._user, field, self.attrs[value][0])
            except (KeyError, IndexError):
                pass


    def _get_or_create_user(self, force_populate=False):
        """
        Loads the User model object from the database or creates it if it
        doesn't exist. Also populates the fields, subject to
        AUTH_LDAP_ALWAYS_UPDATE_USER.
        """
        save_user = False

        username = self.backend.ldap_to_django_username(self._username)

        (self._user, created) = self.backend.get_or_create_user(username, self)

        if created:
            self._user.set_unusable_password()
            save_user = True

        if(force_populate or ldap_settings.AUTH_LDAP_ALWAYS_UPDATE_USER or created):
            self._populate_user()
            self._populate_and_save_user_profile()

            #self._populate_profile_from_group_memberships()
            save_user = True

        if ldap_settings.AUTH_LDAP_MIRROR_GROUPS:
            self._mirror_groups()

        if save_user:
            self._user.save()

        self._user.ldap_user = self
        self._user.ldap_username = self._username

    def _mirror_groups(self):

        groups_configs = self._get_groups_for_mirroring()

        groups = [Group.objects.get_or_create(name=group_config.name)[0] for group_config
            in groups_configs]

        self._user.groups = groups

    def _get_groups_for_mirroring(self):
        group_dns = self._get_groups()._get_group_dns()
        group_configs = LDAPGroupConfig.objects.all()

        allowed_configs = []
        for group_config in group_configs:
            if ldap.dn.str2dn(group_config.group_dn) in [ldap.dn.str2dn(group_dn) for group_dn in group_dns]:
                allowed_configs.append(group_config)
        return allowed_configs


    def _populate_and_save_user_profile(self):
        """
        Populates a User profile object with fields from the LDAP directory.
        """
        try:
            profile = models.UserProfile.objects.get(user=self._user)
            self._populate_profile_fields(profile)

            if len(ldap_settings.AUTH_LDAP_USER_ATTR_MAP) > 0:
                profile = self._populate_profile_fields(profile)
                profile.save()
        except (SiteProfileNotAvailable, ObjectDoesNotExist), e:
            profile = models.UserProfile(user=self._user,
                                         role=models.UserProfile.ROLE_USER,
                                         ldap_user=True)
            

            profile = self._populate_profile_fields(profile)

            profile.save()

    def _populate_profile_fields(self, profile):
        for field, attr in ldap_settings.AUTH_LDAP_USER_ATTR_MAP.iteritems():
                try:
                    # user_attrs is a hash of lists of attribute values
                    setattr(profile, field, self.attrs[attr][0])
                except (KeyError, IndexError), e:
                    pass
        return profile

    def _check_required_group(self):
        """
        Returns True if the group requirement (AUTH_LDAP_REQUIRE_GROUP) is
        met. Always returns True if AUTH_LDAP_REQUIRE_GROUP is None.
        """
        required_groups_dns = ldap_settings.AUTH_LDAP_REQUIRE_GROUPS

        if required_groups_dns:
            is_member = False
            for required_group_dn in required_groups_dns:
                try:
                    is_member = self._get_groups().is_member_of(required_group_dn.group_dn)
                except self.ldap.LDAPError:
                    pass

                if is_member:
                    break

            if not is_member:
                raise self.AuthenticationFailed("User is not a member of AUTH_LDAP_REQUIRE_GROUP")

    """
    def _populate_profile_from_group_memberships(self):
        for group_dn in ldap_settings.AUTH_LDAP_REQUIRE_GROUPS:
            if self._get_groups().is_member_of(group_dn.group_dn) and group_dn.is_admin:
                self._user.get_profile().role=models.UserProfile.ROLE_ADMIN
                self._user.get_profile().save()
                break
    """

    def _get_groups(self):
        """
        Returns an _LDAPUserGroups object, which can determine group
        membership.
        """
        if self._groups is None:
            self._groups = PlatoUserGroups(self)

        return self._groups

class PlatoUserGroups(_LDAPUserGroups):

    def __init__(self, ldap_user):
        try:
            super(PlatoUserGroups, self).__init__(ldap_user)
        except ImproperlyConfigured:
            self._init_group_settings()

    def _init_group_settings(self):
        """
        Loads the settings we need to deal with groups. Raises
        ImproperlyConfigured if anything's not right.
        """
        self._group_type = ldap_settings.AUTH_LDAP_GROUP_TYPE
        if self._group_type is None:
            raise ImproperlyConfigured("AUTH_LDAP_GROUP_TYPE must be an LDAPGroupType instance.")

        self._group_search = ldap_settings.AUTH_LDAP_GROUP_SEARCH
        if self._group_search is None:
            raise ImproperlyConfigured("AUTH_LDAP_GROUP_SEARCH must be an LDAPSearch instance.")

    """
    def _get_group_dns(self):
        Returns a (cached) set of the distinguished names in self._group_infos.
        return super(PlatoUserGroups, self)._get_group_dns()
    """

class PlatoLDAPSettings(LDAPSettings):

    defaults = {
        'AUTH_LDAP_ALWAYS_UPDATE_USER': True,
        'AUTH_LDAP_AUTHORIZE_ALL_USERS': False,
        'AUTH_LDAP_BIND_DN': '',
        'AUTH_LDAP_BIND_PASSWORD': '',
        'AUTH_LDAP_CACHE_GROUPS': False,
        'AUTH_LDAP_CONNECTION_OPTIONS': {},
        'AUTH_LDAP_FIND_GROUP_PERMS': False,
        'AUTH_LDAP_GLOBAL_OPTIONS': {},
        'AUTH_LDAP_GROUP_CACHE_TIMEOUT': None,
        'AUTH_LDAP_GROUP_SEARCH': None,
        'AUTH_LDAP_GROUP_TYPE': None,
        'AUTH_LDAP_GROUP_OBJECT_CLASS': None,
        'AUTH_LDAP_MIRROR_GROUPS': False,
        'AUTH_LDAP_PROFILE_ATTR_MAP': {},
        'AUTH_LDAP_REQUIRE_GROUP': None,
        'AUTH_LDAP_REQUIRE_GROUPS': [],
        'AUTH_LDAP_SERVER_URI': 'ldap://localhost',
        'AUTH_LDAP_START_TLS': False,
        'AUTH_LDAP_USER_ATTR_MAP': {},
        'AUTH_LDAP_USER_DN_TEMPLATE': None,
        'AUTH_LDAP_USER_FLAGS_BY_GROUP': {},
        'AUTH_LDAP_USER_SEARCH': None,
        'AUTH_LDAP_IS_USED': False,
        'AUTH_LDAP_USER_DISCRIMINANT': 'uid',
        'AUTH_LDAP_USERS_DN': None,
        'AUTH_LDAP_GROUPS_DN': None
    }

    def _set_up_groups(self):
        if self.AUTH_LDAP_GROUPS_DN and self.AUTH_LDAP_GROUP_TYPE and self.AUTH_LDAP_GROUP_OBJECT_CLASS:
            self.AUTH_LDAP_GROUP_SEARCH = LDAPSearch(self.AUTH_LDAP_GROUPS_DN,\
                                                     ldap.SCOPE_SUBTREE,
                                                     "(objectClass=%s)"%self.AUTH_LDAP_GROUP_OBJECT_CLASS)


    def __init__(self):
        super(PlatoLDAPSettings, self).__init__()

        require_groups = LDAPGroupConfig.objects.all()
        if require_groups:
            self.AUTH_LDAP_REQUIRE_GROUPS = require_groups

        for ldap_config in ConfigEntry.objects.\
                    filter(config_key__in=ConfigEntry.AUTH_LDAP_CONFIGS):
            setattr(self, ldap_config.config_key, ldap_config.config_val)

        if self.AUTH_LDAP_USERS_DN:
            self.AUTH_LDAP_USER_SEARCH = LDAPSearch(self.AUTH_LDAP_USERS_DN,\
                                                    ldap.SCOPE_SUBTREE, "(%(discriminant)s=%(user)s)")

        for ldap_config in ConfigEntry.objects.\
                filter(config_key__in=ConfigEntry.AUTH_LDAP_USER_ATTRS):
            self.AUTH_LDAP_USER_ATTR_MAP[ConfigEntry.AUTH_LDAP_USER_ATTRS_MAP[ldap_config.config_key]] = ldap_config.config_val

        group_type = get_entry(ConfigEntry.AUTH_LDAP_GROUP_OBJECT_CLASS)
        if group_type:
            self.AUTH_LDAP_GROUP_TYPE = getattr(config,ConfigEntry.GROUPS_CLASSES[group_type.config_val])()

        self._set_up_groups()



ldap_settings = PlatoLDAPSettings()