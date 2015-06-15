window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null;

function updateValues( response ) {

  // Update the relevant parts of the page given the JSON response,
  // and reset the button states for a new entry.

  $( "#id_chain" ).val(response.chain);
  $( "#id_parent" ).val(response.parent);
  $( "#sound" ).attr("src", response.url);
  $( "#status" ).text(response.status);

  $( "#record" ).addClass("unavailable");
  $( "#submit" ).prop("disabled", true);
  $( "#listen" ).removeClass("active");
  $( "#record" ).removeClass("active");

  updateMessage("");

}

function micShared() {

  $( "#share" ).addClass("active");
  $( "#record" ).removeClass("unavailable");
  updateMessage("");

}

function postEntry( blob ) {

  // Post the entry via AJAX.
  //
  // Grab the data in the form, put it in a FormData object,
  // append the blob, and submit it.

  var entryForm = document.getElementById("entry");
  var formData = new FormData(entryForm);
  formData.append("audio", blob);

  $.ajax({
    url: $("#entry").attr("action"), // get
    type: "POST",
    data: formData,
    processData: false,
    contentType: false,
    success: function(response) {

      // The server responds with the URL of the completion page
      // or the values to update for the next entry.

      if (response.complete) {
        window.location.replace(response.complete);
      } else {
        $( "#status" ).text("Success!");
        $( "#status" ).addClass("bg-success");

        setTimeout(function() {
          $( "#status" ).removeClass("bg-success");
          updateValues(response);
        }, 2000);  // show success message for 2 seconds
      }

    },
    error: function(xhr, msg, err) {
      updateMessage("There was a problem processing your entry");
    }
  });
}

$( "#share" ).click(function( event ) {

  // Get permission to get the audio stream
  // and make the audioRecorder object.

  if (!audioRecorder) {
    // connect the audio and change the button state
    connectAudio( micShared );
    sharedRecorder();
  } else {
    audioRecorder = null;
    $( "#share" ).removeClass("active");
    updateMessage("");
  }

});

function sharedRecorder() {

  // Called after audio is connected.

  if ($("#sound").attr("src")) {
    $("#listen").removeClass("unavailable");
  } else {
    listenedToSound();
  }
}

$( "#sound" ).bind("ended", function() {

  // Update to indicate that the sound is done playing

  $("#listen").removeClass("active");
  listenedToSound();

});

function listenedToSound() {

  // Called after the audio is listened to
  // or when audio isn't available

  $("#listen").addClass("played");

  if( $("#record").hasClass("unavailable") ) {
    $("#record").removeClass("unavailable");
  }

}

$( "#listen" ).click(function( event ) {

  // Trigger the (hidden) audio element.
  //
  // If the speaker is available and you're not making a recording,
  // play or pause the audio.

  if( $(this).hasClass("unavailable") ) {
    updateMessage("Share your microphone to play.");
    return;
  } else if( $("#record").hasClass("active") ) {
    updateMessage("You can't record the original sound.");
    return;
  } else {
    $(this).toggleClass("active");
    updateMessage("");
  }

  if( $(this).hasClass("active") ) {
    $( "#sound" ).trigger("play");
  } else {
    $( "#sound" ).trigger("pause");
  }

});


$( "#record" ).click(function( event ) {

  // Toggle the audio recorder.
  //
  // If the recorder is available and the sound is not playing,
  // turn the recorder on and off.

  if( !audioRecorder ) {
    updateMessage("Share your microphone to play.");
    return;
  } else if( !$("#listen").hasClass("played") ) {
    updateMessage("You have to listen to the sound first.");
    return;
  } else if( $("#listen").hasClass("active") ) {
    updateMessage("You can't record the original sound.");
    return;
  } else {
    updateMessage("");
    $( this ).toggleClass("active");
  }

  if( $(this).hasClass("active") ) {
    audioRecorder.clear();
    audioRecorder.record();
  } else {
    audioRecorder.stop();
    $("#submit").prop("disabled", false);
  }

});

$( "#entry" ).submit(function( event ) {

  // Gather the audio and submit the form with AJAX.
  // If there isn't an audioRecorder, try to submit
  // the form normally (used for testing only).

  updateMessage("");

  if (audioRecorder) {
    event.preventDefault();
    audioRecorder.getBuffers();
    audioRecorder.exportWAV( postEntry );
  } else {
    console.log('No audioRecorder so trying non-ajax post');
  }

});

function updateMessage( msg ) {

  // Sets/clears the message queue.

  $( "#message" ).text(msg);

}

function connectAudio( callback ) {
  if (!navigator.getUserMedia) {
    navigator.getUserMedia = navigator.webkitGetUserMedia ||
                             navigator.mozGetUserMedia;
  }

  navigator.getUserMedia(
    {audio: true},
    function(stream) {
      audioInput = audioContext.createMediaStreamSource(stream);
      audioRecorder = new Recorder( audioInput, {workerPath: recorderWorkerPath} );
      callback();
    },
    function(err) {
      updateMessage("There was a problem sharing your mic");
    }
  );
}
