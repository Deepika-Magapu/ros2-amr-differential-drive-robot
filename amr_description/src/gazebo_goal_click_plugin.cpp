#include <ignition/gui/Plugin.hh>
#include <ignition/gui/GuiEvents.hh>
#include <ignition/gui/Application.hh>
#include <ignition/plugin/Register.hh>
#include <ignition/transport/Node.hh>
#include <ignition/msgs/vector3d.pb.h>
#include <ignition/common/Console.hh>

class GazeboGoalClick : public ignition::gui::Plugin
{
  Q_OBJECT

public:
  GazeboGoalClick()
  {
    pub_ = node_.Advertise<ignition::msgs::Vector3d>("/gazebo_click_point");
    if (ignition::gui::App())
    {
      ignition::gui::App()->installEventFilter(this);
    }
    ignmsg << "[GazeboGoalClick] Plugin initialized. Listening for 3D scene clicks." << std::endl;
  }

  virtual ~GazeboGoalClick() override = default;

  bool eventFilter(QObject *_obj, QEvent *_event) override
  {
    if (_event && _event->type() == ignition::gui::events::LeftClickToScene::kType)
    {
      auto leftClick = static_cast<ignition::gui::events::LeftClickToScene *>(_event);
      auto pt = leftClick->Point();
      ignition::msgs::Vector3d msg;
      msg.set_x(pt.X());
      msg.set_y(pt.Y());
      msg.set_z(pt.Z());
      pub_.Publish(msg);
      ignmsg << "[GazeboGoalClick] Floor click: x=" << pt.X() << ", y=" << pt.Y() << std::endl;
    }
    return ignition::gui::Plugin::eventFilter(_obj, _event);
  }

private:
  ignition::transport::Node node_;
  ignition::transport::Node::Publisher pub_;
};

IGNITION_ADD_PLUGIN(GazeboGoalClick, ignition::gui::Plugin)

#include "gazebo_goal_click_plugin.moc"

