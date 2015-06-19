window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null;

//$(function () {

$("#share").click(function () {
  if (!navigator.getUserMedia) {
    navigator.getUserMedia = navigator.webkitGetUserMedia ||
                             navigator.mozGetUserMedia;
  }

  if (!audioRecorder) {
    navigator.getUserMedia(
      {audio: true},
      function (stream) {
        audioInput = audioContext.createMediaStreamSource(stream);
        audioRecorder = new Recorder(audioInput, {workerPath: recorderWorkerPath});
        $(this).addClass("active");

        if ($("#sound").attr("src")) {
          $("#listen").removeClass("unavailable");
          $("#listen").removeClass("played");
          $("#record").addClass("unavailable");
        } else {
          $("#listen").addClass("unavailable");
          $("#listen").addClass("played");
          $("#record").removeClass("unavailable");
        }
      },
      function (err) {
        console.log(err);
        updateMessage("There was a problem sharing your mic.");
      }
    );
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
        $("#submit").prop("disabled", false);
      }

      return;
    }
  }
});

$("#submit").click(function (event) {
  event.preventDefault();

  audioRecorder.getBuffers();
  audioRecorder.exportWAV(function (blob) {
    var entryForm = $("#entry"),
        formData = new FormData(entryForm),
        formAction = $("#entry").attr("action");

    formData.append("audio", blob);

    $.ajax({
      url: formAction,
      type: "POST",
      data: formData,
      processData: false,
      contentType: false,
      success: function (response) {
        console.log("success");
        console.log(response);

        // update values here
      },
      error: function (xhr, msg, error) {
        console.log("error");
        console.log(error);
      }
    });
  });

});
//});
