window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null,
    audioRecorder = null;

function showAlert(msg, type) {
  var alert = $("#alert");
  alert.text(msg);
  alert.addClass(type);

  setTimeout(function () {
    alert.text("");
    alert.removeClass(type);
  }, 3000);
}

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
      showAlert("There was a problem sharing your mic.", "alert-danger");
    }
  );
}

function setPlayer() {
  if ($("#sound").attr("src")) {

    if (audioRecorder) {
      $("#listen").removeClass("unavailable");
    }

    $("#listen").removeClass("played");
    $("#record").addClass("unavailable");
  } else {
    $("#listen").addClass("unavailable");
    $("#listen").addClass("played");

    if (audioRecorder) {
      $("#record").removeClass("unavailable");
    }
  }
}

function shareMic() {
  if (!audioRecorder) {
    connectAudio();
  } else {
    audioRecorder = null;
    $("#share").removeClass("active");
  }
}

function listenToMessage() {
  if (!$("#sound").attr("src")) {
    showAlert("No messages to listen to.", "alert-info");
    return;
  } else {
    if ($(this).hasClass("unavailable")) {
      showAlert("Share your microphone to play.", "alert-danger");
      return;
    } else {
      $(this).toggleClass("button-on");

      if ($(this).hasClass("button-on")) {
        $("#sound").trigger("play");
      } else {
        $("#sound").trigger("pause");
      }
    }
  }
}

function toggleRecording() {
  if (!$("#listen").hasClass("played")) {
    showAlert("You have to listen to the message to know what to imitate.", "alert-danger");
    return;
  } else {
    $("#record").toggleClass("button-on");

    if ($("#record").hasClass("button-on")) {
      audioRecorder.clear();
      audioRecorder.record();
    } else {
      audioRecorder.stop();
      audioRecorder.exportWAV();
    }

    return;
  }
}
