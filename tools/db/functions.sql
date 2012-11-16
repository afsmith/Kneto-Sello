Create language 'plpgsql';



create or replace function lesson_duration_for_user(user_id numeric, course_id numeric)
returns interval as '
declare
lesson_length interval;
begin
select sum(tracking2.created_on - tracking1.created_on) into lesson_length
from tracking_trackingevent tracking1
join tracking_trackingevent tracking2 on tracking2.parent_event_id = tracking1.id
join content_segment segment on segment.id = tracking1.segment_id
where tracking1.participant_id = user_id
and tracking1.event_type = ''START''
and segment.course_id = course_id;
return lesson_length;
end;' language 'plpgsql';



create or replace function segment_duration_for_user(user_id numeric, segment_id numeric)
returns interval as '
declare
segment_length interval;
begin
select sum(tracking2.created_on - tracking1.created_on) into segment_length
from tracking_trackingevent tracking1
join tracking_trackingevent tracking2 on tracking2.parent_event_id = tracking1.id
where tracking1.participant_id = user_id
and tracking1.event_type = ''START''
and tracking1.segment_id = segment_id
and tracking2.segment_id = segment_id;
return segment_length;
end;' language 'plpgsql';

CREATE OR REPLACE FUNCTION lesson_complete_for_user(course_id numeric, user_id numeric)
  RETURNS character varying AS
$BODY$
DECLARE
module_seg_count integer;
user_seg_count integer;
module_complete varchar;
BEGIN

SELECT 
  COUNT(DISTINCT content_segment.file_id)
  into module_seg_count
FROM 
  public.content_course, 
  public.content_coursegroup, 
  public.content_segment, 
  public.content_file
WHERE 
  content_course.id = content_coursegroup.course_id AND
  content_coursegroup.course_id = content_segment.course_id AND
  content_segment.file_id = content_file.id AND
  content_course.id = course_id AND 
  content_file."type" != 30;

SELECT 
  COUNT(DISTINCT content_segment.file_id)
  into user_seg_count
FROM 
  public.tracking_trackingevent, 
  public.content_segment, 
  public.content_file_groups
WHERE 
  content_segment.id = tracking_trackingevent.segment_id AND
  content_file_groups.file_id = content_segment.file_id AND
  tracking_trackingevent.participant_id = user_id AND 
  content_segment.course_id = course_id AND 
  tracking_trackingevent.lesson_status = 'completed';

  module_complete := 'Incomplete' ;

IF module_seg_count =  user_seg_count 
THEN module_complete := 'Complete' ;
END IF;
RETURN module_complete;
END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


CREATE OR REPLACE FUNCTION receiver_count()  RETURNS character varying AS
$BODY$
DECLARE
receiver integer;
BEGIN

SELECT 
  COUNT(*)
  into receiver
FROM 
  public.auth_user, 
    public.management_userprofile
WHERE 
  auth_user.id = management_userprofile.user_id and 
  public.management_userprofile.role = 30;

RETURN receiver;

END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;


CREATE OR REPLACE FUNCTION publisher_count()  RETURNS character varying AS
$BODY$
DECLARE
publisher integer;
BEGIN

SELECT 
  COUNT(*)
  into publisher
FROM 
  public.auth_user, 
    public.management_userprofile
WHERE 
  auth_user.id = management_userprofile.user_id and 
  public.management_userprofile.role = 20;
     
RETURN publisher ;

END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE OR REPLACE FUNCTION super_count()  RETURNS character varying AS
$BODY$
DECLARE
super integer;
BEGIN

SELECT 
  COUNT(*)
  into super
FROM 
  public.auth_user, 
    public.management_userprofile
WHERE 
  auth_user.id = management_userprofile.user_id and 
  public.management_userprofile.role = 10;

 super := (super - 1) ;

RETURN super;

END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;

CREATE OR REPLACE FUNCTION total_admin_count()  RETURNS character varying AS
$BODY$
DECLARE
publisher integer;super integer;
total integer;


BEGIN


SELECT
  COUNT(*)
  into publisher
FROM
  public.auth_user,
    public.management_userprofile
WHERE
  auth_user.id = management_userprofile.user_id and
  public.management_userprofile.role = 20;


SELECT
  COUNT(*)
  into super
FROM
  public.auth_user,
    public.management_userprofile
WHERE
  auth_user.id = management_userprofile.user_id and
  public.management_userprofile.role = 10;


 super := (super - 1) ;
 total := (super + publisher);


RETURN total;


END ; $BODY$
  LANGUAGE plpgsql VOLATILE
  COST 100;




