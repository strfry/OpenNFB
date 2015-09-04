import QtQuick 2.0
import QtMultimedia 5.0

Rectangle {
    //width: 300
    //height: 300
    color: "black"
    anchors.fill: parent

    property real brightness: 0.5
    property real speed: 1.0
    property real volume: 1.0

    MediaPlayer {
        id: mediaPlayer
        source: "../test.mp4"
        autoPlay: true
        //volume: parent.volume
        //playbackRate: parent.volume
    }

    onVolumeChanged: {
        mediaPlayer.volume = Math.min(Math.max(volume, 0.2), 1.0);
    }
    
    onSpeedChanged: {
        var speed_ = Math.min(Math.max(speed*4, 1.0), 4.0)
        //mediaPlayer.playbackRate = speed_
    }

    onBrightnessChanged: {
        var newOpacity = 1.0 - Math.min(Math.max(brightness, 0.0), 1.0);

        overlay.opacity = 0.9 * overlay.opacity + 0.1 * newOpacity;

        //console.log('opacity changed to', overlay.opacity)
    }
    
    
    VideoOutput {
        id: video
        anchors.fill: parent
        source: mediaPlayer
    }
    

    
    Rectangle {
        id: overlay
        color: "black"
        anchors.fill: parent
        //opacity: 1.0 - Math.min(Math.max(parent.brightness, 0.0), 1.0);
    }
    

    /*
    ShaderEffect {
        property variant source: ShaderEffectSource { sourceItem: video; hideSource: true }
        property real brightness: parent.brightness
        anchors.fill: video

        fragmentShader: "
            varying highp vec2 qt_TexCoord0;
            uniform sampler2D source;
            uniform highp float brightness;
            void main(void)
            {
                highp vec2 wiggledTexCoord = qt_TexCoord0;
                //gl_FragColor = vec4(1.0) - texture2D(source, wiggledTexCoord.st) * brightness;
                gl_FragColor = vec4(brightness);
            }
        "
    }
    */
}
