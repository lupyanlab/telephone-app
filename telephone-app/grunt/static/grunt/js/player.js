window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null,
    audioRecorder = null;

function connectAudio(callback) {

  // Create an audio recorder object

  if (!navigator.getUserMedia) {
    navigator.getUserMedia = navigator.webkitGetUserMedia ||
                             navigator.mozGetUserMedia;
  }

  navigator.getUserMedia(
    {audio: true},
    function (stream) {
      audioInput = audioContext.createMediaStreamSource(stream);
      audioRecorder = new Recorder(audioInput, config);

      $("#share").addClass("active");
      setPlayer();
    },
    function (error) {
      console.log(error);
      updateMessage("There was a problem sharing your mic.");
    }
  );
}

function setPlayer(src) {
  if (src) {
    $("#sound").attr("src", src);
    $("#listen").removeClass("unavailable");
    $("#listen").removeClass("played");
    $("#record").addClass("unavailable");
  } else {
    $("#sound").attr("src", "");
    $("#listen").addClass("unavailable");
    $("#listen").addClass("played");
    $("#record").removeClass("unavailable");
  }
}

$(function () {

  $("#share").click(function () {
    if (!audioRecorder) {
      connectAudio();
    } else {
      audioRecorder = null;
      $(this).removeClass("active");
    }
  });

  $("#listen").click(function () {
    if (!$("#sound").attr("src")) {
      updateMessage("There is nothing to listen to.");
      return;
    } else {
      if ($(this).hasClass("unavailable")) {
        updateMessage("Share your microphone to play.");
        return;
      } else {
        $(this).toggleClass("active");

        if ($(this).hasClass("active")) {
          $("#sound").trigger("play");
        } else {
          $("#sound").trigger("pause");
        }

        return;
      }
    }
  });

  $("#sound").bind("ended", function () {
    $("#listen").removeClass("active");
    $("#listen").addClass("played");
    $("#record").removeClass("unavailable");
  });

  $("#record").click(function () {
    if ($(this).hasClass("unavailable")) {
      updateMessage("Share your microphone to play.");
      return;
    } else {
      if (!$("#listen").hasClass("played")) {
        updateMessage("Listen to the message before making your recording.");
        return;
      } else {
        $(this).toggleClass("active");

        if ($(this).hasClass("active")) {
          audioRecorder.clear();
          audioRecorder.record();
        } else {
          audioRecorder.stop();
          audioRecorder.exportWAV();
        }

        return;
      }
    }
  });

});
