window.AudioContext = window.AudioContext || window.webkitAudioContext;

var audioContext = new AudioContext(),
    audioInput = null;

$( "#share" ).click(function( event ) {

    // Get permission to get the audio stream
    // and make the audioRecorder object.

    if (!audioRecorder) {
        // connect the audio and change the button state
        connectAudio( micShared );
    } else {
        audioRecorder = null;
        $( "#share" ).removeClass("active");
        updateMessage("");
    }

});

$( "#sound" ).bind("ended", function() {

    // Update to indicate that the sound is done playing

    $("#listen").removeClass("active");
    if( $("#record").hasClass("unavailable") ) {
        $("#record").removeClass("unavailable");
    }

});

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
    } else if( $(this).hasClass("unavailable") ) {
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
            audioRecorder = new Recorder( audioInput, cfg );
            callback();
        },
        function(err) {
            updateMessage("There was a problem sharing your mic");
        }
    );
}
