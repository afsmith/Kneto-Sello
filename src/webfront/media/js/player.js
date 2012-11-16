$(document).ready(function(){
  // -- registering handlers
  app.player.api.register('app.callbacks.fp.info_handler', 'info');
  app.player.api.register('app.callbacks.fp.error_handler', 'error');
  app.player.api.register('app.callbacks.fp.exception_handler', 'exception');
  app.player.api.register('app.callbacks.fp.keypress_handler', 'keypress');
  app.player.api.register('app.callbacks.fp.pdf_handler', 'defaultClick');
  app.player.api.register('app.callbacks.fp.activeItem_handler', 'setActive');
  app.player.api.register('app.callbacks.fp.this_is_finished', 'thisIsFinished');
  app.player.api.register('app.callbacks.fp.pdf_handler', 'showPDF');
  app.player.api.register('app.callbacks.fp.scorm_handler', 'showSCORM');
  app.player.api.register('app.callbacks.fp.html_handler', 'showHTML');
  app.player.api.register('app.callbacks.fp.pdf_handler', 'showPPT');
  app.player.api.register('app.callbacks.fp.pdf_handler', 'showDOC');
  app.player.api.register('app.callbacks.fp.html_handler', 'showText');
});
// -- flash embedding
function playMovie(url, type, time, index, duration){
    if(!time){
    var time = 10;
  }
  if(!duration){
      duration = 0;
  }
  var flashvars = {
      'contentURL'      : encodeURIComponent(url),
      'cType'           : type,
      'time'            : time,
      'relativeURL'     : mediaURL,
      'playingIndex'    : playingIndex,
      'duration'        : duration,
      'siteLanguage': siteLanguage
  };

  var playerHeight = 286;
  var playerWidth = 400;
  var minPlayerHeight = 480;
  var minPlayerWidth = 856;
  var maxPlayerHeight = 600;
  var maxPlayerWidth = 856;
  var ratio = 1.4;

  $(window).resize(function() {
    calculateNewDimensions();
  });

  function calculateNewDimensions() {
    if ( $('#videoWrapper').length ) {
      var newPlayerHeight = $(window).height() - 450;
      if (newPlayerHeight <= minPlayerHeight) {
        playerHeight = minPlayerHeight;
      }
      else if (newPlayerHeight <= maxPlayerHeight) {
        playerHeight = newPlayerHeight
      }
      var newPlayerWidth = Math.round(1.4 * playerHeight);
      if ( ( newPlayerWidth >= minPlayerWidth) && ( newPlayerWidth <= maxPlayerWidth ) ) {
        playerWidth = Math.round(ratio * playerHeight);
      }
      else {
        playerWidth = minPlayerWidth;
      }
      $('#videoWrapper').height(playerHeight);
      $('#videoWrapper').width(playerWidth);
      $('#video').attr('height', playerHeight);
      $('#video').attr('width', playerWidth);
    };
  }

  calculateNewDimensions();

  var params = {'allowFullscreen': 'true', 'allowScriptAccess': 'always', 'wmode': 'transparent'};
  swfobject.embedSWF(mediaURL + "swf/player.swf", "video", playerWidth, playerHeight, "9.0.0", false, flashvars, params, {});
  return false;

}
