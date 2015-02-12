window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null,
    audioRecorder = null;

$( "#share" ).click(function( event ) {

    // Get permission to get the audio stream
    // and make the audioRecorder object.

    if (!audioRecorder) {
        // connect the audio and change the button state
        connectAudio(function() {
            $( "#share" ).addClass("active");
            updateMessage();
        });
    } else {
        audioRecorder = null;
        $( "#share" ).removeClass("active");
    }

});

$( "#sound" ).bind("ended", function() {

    // Update to indicate that the sound is done playing

    $( "#phone" ).removeClass("playing");

});

$( "#play" ).click(function( event ) {

    // Trigger the (hidden) audio element.
    //
    // TODO:
    // * work on chrome and safari
    // * prevent playing more than once

    $( "#sound" ).trigger("play");
    $( "#phone" ).addClass("playing");

});


$( "#record" ).click(function( event ) {

    // Toggle the audio recorder.
    //
    // TODO:
    // * make the submit button available after making a recording

    if (!audioRecorder) {
        $( "#message" ).text("Share your microphone to make a recoding");
        return;
    }

    $( "#phone" ).toggleClass("recording");

    if ($( "#phone" ).hasClass("recording")) {
        audioRecorder.clear();
        audioRecorder.record();
    } else {
        audioRecorder.stop();
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
            audioRecorder = new Recorder( audioInput, cfg );
            callback();
        },
        function(err) {
            updateMessage("There was a problem sharing your mic");
        }
    );
}
