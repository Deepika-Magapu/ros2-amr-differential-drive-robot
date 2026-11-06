import QtQuick 2.12
import QtQuick.Controls 2.5
import QtQuick.Layouts 1.12

Rectangle {
  implicitWidth: 320
  implicitHeight: 45
  color: "#1e222a"
  radius: 6
  border.color: "#3e4451"
  border.width: 1

  RowLayout {
    anchors.fill: parent
    anchors.margins: 8
    spacing: 10

    Rectangle {
      width: 14
      height: 14
      radius: 7
      color: "#98c379"
      Layout.alignment: Qt.AlignVCenter
    }

    Label {
      text: "Click any floor point in Gazebo to navigate"
      color: "#abb2bf"
      font.pixelSize: 12
      font.bold: true
      Layout.fillWidth: true
      verticalAlignment: Text.AlignVCenter
    }
  }
}

