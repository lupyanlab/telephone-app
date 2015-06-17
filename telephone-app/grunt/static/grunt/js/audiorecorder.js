window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null;

function connectAudio(callback) {

  // Create a Recorder.js object
  //
  // Requires "recorderWorkerPath" to be set.

  if (!navigator.getUserMedia) {
    navigator.getUserMedia = navigator.webkitGetUserMedia ||
                             navigator.mozGetUserMedia;
  }

  navigator.getUserMedia(
    {audio: true},
    function(stream) {
      audioInput = audioContext.createMediaStreamSource(stream);
      audioRecorder = new Recorder(audioInput, {workerPath: recorderWorkerPath});
      callback();
    },
    function(err) {
      updateMessage("There was a problem sharing your mic");
    }
  );
}


function postEntry(blob) {

  // Post the entry via AJAX.
  //
  // Grab the data in the form, put it in a FormData object,
  // append the blob from recorder.js, and submit it.

  var entryForm = document.getElementById("entry"),
      formData = new FormData(entryForm),
      formAction = $("#entry").attr("action");

  formData.append("audio", blob);

  $.ajax({
    url: formAction,
    type: "POST",
    data: formData,

    // sending raw data, so don't process or label
    processData: false,
    contentType: false,

    success: function(response) {

      // The server responds with the URL of the completion page
      // or the values to update for the next entry.

      if (response.complete) {
        window.location.replace(response.complete);
      } else {
        $("#status").text("Success!");
        $("#status").addClass("bg-success");

        updateValues(response);

        // show success message for 2 seconds
        setTimeout(function() {
          $("#status").text("");
          $("#status").removeClass("bg-success");
        }, 2000);
      }

    },
    error: function(xhr, msg, err) {
      updateMessage("Whoops! There was a problem processing your entry");
    }
  });
}

function updateValues(response) {

  // Update the relevant parts of the page given the JSON response,
  // and reset the button states for a new entry.

  if (response.url) {
    $("#sound").attr("src", response.url);
    $("#record").addClass("unavailable");
  } else {
    #("#sound").attr("src", "");
  }

  $("#submit").prop("disabled", true);

  $("#listen").removeClass("active");
  $("#record").removeClass("active");

  updateMessage("");
}



$("#share").click(function (event) {

  // Get permission to get the audio stream
  // and make the audioRecorder object.

  if (!audioRecorder) {
    // connect the audio and change the button state
    connectAudio(micShared);
    updateMessage("");
  } else {
    audioRecorder = null;
    $("#share").removeClass("active");
    updateMessage("");
  }

});

function micShared() {

  $("#share").addClass("active");
  updatePlayerState();

}

function updatePlayerState() {

  if ($("#sound").attr("src")) {
    $("#listen").removeClass("unavailable");
    $("#record").addClass("unavailable");
  } else {
    listenedToSound();
  }

}

$("#sound").bind("ended", function () {

  // Update to indicate that the sound is done playing

  $("#listen").removeClass("active");
  listenedToSound();

});

function listenedToSound() {

  // Called after the audio is listened to
  // or when audio isn't available

  $("#listen").addClass("played");

  if($("#record").hasClass("unavailable")) {
    $("#record").removeClass("unavailable");
  }

}

$("#listen").click(function (event) {

  // Trigger the (hidden) audio element.
  //
  // If the speaker is available and you're not making a recording,
  // play or pause the audio.

  if ($(this).hasClass("unavailable")) {
    if ($("#sound").attr("src")) {
      // Sound is present, but the player is inactive
      updateMessage("Share your microphone to play.");
    } else {
      // No sound is present, so make a seed recording
      updateMessage("There is nothing to listen to.");
    }
    return;
  } else {
    if ($("#record").hasClass("active")) {
      updateMessage("You can't record the original sound.");
      return;
    } else {
      // Toggle the listener
      $(this).toggleClass("active");
      updateMessage("");
  }

  if ($(this).hasClass("active")) {
    $("#sound").trigger("play");
  } else {
    $("#sound").trigger("pause");
  }

});


$( "#record" ).click(function( event ) {

  // Toggle the audio recorder.
  //
  // If the recorder is available and the sound is not playing,
  // turn the recorder on and off.

  if (!audioRecorder) {
    updateMessage("Share your microphone to play.");
    return;
  } else if(!$("#listen").hasClass("played")) {
    updateMessage("You have to listen to the sound first.");
    return;
  } else if($("#listen").hasClass("active")) {
    updateMessage("You can't record the original sound.");
    return;
  } else {
    // Toggle the recorder
    updateMessage("");
    $(this).toggleClass("active");
  }

  if ($(this).hasClass("active")) {
    audioRecorder.clear();
    audioRecorder.record();
  } else {
    audioRecorder.stop();
    $("#submit").prop("disabled", false);
  }

});

$("#entry").submit(function (event) {

  // Gather the audio and submit the form with AJAX.
  // If there isn't an audioRecorder, try to submit
  // the form normally (used for testing only).

  updateMessage("");

  if (audioRecorder) {
    event.preventDefault();
    audioRecorder.getBuffers();
    audioRecorder.exportWAV(postEntry);
  } else {
    console.log('No audioRecorder so trying non-ajax post');
  }

});

function updateMessage(msg) {

  // Sets/clears the message queue.

  $("#message").text(msg);

}
