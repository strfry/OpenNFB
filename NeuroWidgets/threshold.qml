import QtQuick 2.0
import QtMultimedia 5.0

Rectangle {
    property real value: 0.4
    property real threshold: 0.6

    width: 100
    height: 100
    color: "grey"
    border.color: "white"
    border.width: 1
    radius: 10
    opacity: 0.5


    Rectangle {
        anchors {
            bottom: parent.bottom
            bottomMargin: parent.border.width
        }

        x: parent.border.width
        //y:
        width: parent.width - 2 * parent.border.width
        height: (parent.height - 2 * parent.border.width) * value
        color: "red"
        radius: parent.radius
    }

    Rectangle {
        x: 1
        y: (parent.border.width) + ((1.0 - threshold) * (parent.height - parent.border.width)) 
        height: 2
        width: parent.width
        color: "black"
    }


}
