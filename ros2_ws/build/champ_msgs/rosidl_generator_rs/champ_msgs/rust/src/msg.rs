#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};



// Corresponds to champ_msgs__msg__Velocities

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Velocities {

    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angular_z: f32,

}



impl Default for Velocities {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Velocities::default())
  }
}

impl rosidl_runtime_rs::Message for Velocities {
  type RmwMsg = super::msg::rmw::Velocities;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        linear_x: msg.linear_x,
        linear_y: msg.linear_y,
        angular_z: msg.angular_z,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      linear_x: msg.linear_x,
      linear_y: msg.linear_y,
      angular_z: msg.angular_z,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      linear_x: msg.linear_x,
      linear_y: msg.linear_y,
      angular_z: msg.angular_z,
    }
  }
}


// Corresponds to champ_msgs__msg__PID

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PID {

    // This member is not documented.
    #[allow(missing_docs)]
    pub p: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub d: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub i: f32,

}



impl Default for PID {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::PID::default())
  }
}

impl rosidl_runtime_rs::Message for PID {
  type RmwMsg = super::msg::rmw::PID;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        p: msg.p,
        d: msg.d,
        i: msg.i,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      p: msg.p,
      d: msg.d,
      i: msg.i,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      p: msg.p,
      d: msg.d,
      i: msg.i,
    }
  }
}


// Corresponds to champ_msgs__msg__Imu

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Imu {

    // This member is not documented.
    #[allow(missing_docs)]
    pub orientation: geometry_msgs::msg::Quaternion,


    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_acceleration: geometry_msgs::msg::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angular_velocity: geometry_msgs::msg::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub magnetic_field: geometry_msgs::msg::Vector3,

}



impl Default for Imu {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Imu::default())
  }
}

impl rosidl_runtime_rs::Message for Imu {
  type RmwMsg = super::msg::rmw::Imu;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        orientation: geometry_msgs::msg::Quaternion::into_rmw_message(std::borrow::Cow::Owned(msg.orientation)).into_owned(),
        linear_acceleration: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.linear_acceleration)).into_owned(),
        angular_velocity: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.angular_velocity)).into_owned(),
        magnetic_field: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Owned(msg.magnetic_field)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        orientation: geometry_msgs::msg::Quaternion::into_rmw_message(std::borrow::Cow::Borrowed(&msg.orientation)).into_owned(),
        linear_acceleration: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.linear_acceleration)).into_owned(),
        angular_velocity: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.angular_velocity)).into_owned(),
        magnetic_field: geometry_msgs::msg::Vector3::into_rmw_message(std::borrow::Cow::Borrowed(&msg.magnetic_field)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      orientation: geometry_msgs::msg::Quaternion::from_rmw_message(msg.orientation),
      linear_acceleration: geometry_msgs::msg::Vector3::from_rmw_message(msg.linear_acceleration),
      angular_velocity: geometry_msgs::msg::Vector3::from_rmw_message(msg.angular_velocity),
      magnetic_field: geometry_msgs::msg::Vector3::from_rmw_message(msg.magnetic_field),
    }
  }
}


// Corresponds to champ_msgs__msg__Point

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Point {

    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f32,

}



impl Default for Point {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Point::default())
  }
}

impl rosidl_runtime_rs::Message for Point {
  type RmwMsg = super::msg::rmw::Point;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        x: msg.x,
        y: msg.y,
        z: msg.z,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      x: msg.x,
      y: msg.y,
      z: msg.z,
    }
  }
}


// Corresponds to champ_msgs__msg__PointArray

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PointArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub lf: super::msg::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rf: super::msg::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lh: super::msg::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rh: super::msg::Point,

}



impl Default for PointArray {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::PointArray::default())
  }
}

impl rosidl_runtime_rs::Message for PointArray {
  type RmwMsg = super::msg::rmw::PointArray;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        lf: super::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.lf)).into_owned(),
        rf: super::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.rf)).into_owned(),
        lh: super::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.lh)).into_owned(),
        rh: super::msg::Point::into_rmw_message(std::borrow::Cow::Owned(msg.rh)).into_owned(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        lf: super::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.lf)).into_owned(),
        rf: super::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.rf)).into_owned(),
        lh: super::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.lh)).into_owned(),
        rh: super::msg::Point::into_rmw_message(std::borrow::Cow::Borrowed(&msg.rh)).into_owned(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      lf: super::msg::Point::from_rmw_message(msg.lf),
      rf: super::msg::Point::from_rmw_message(msg.rf),
      lh: super::msg::Point::from_rmw_message(msg.lh),
      rh: super::msg::Point::from_rmw_message(msg.rh),
    }
  }
}


// Corresponds to champ_msgs__msg__Joints

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Joints {

    // This member is not documented.
    #[allow(missing_docs)]
    pub position: Vec<f32>,

}



impl Default for Joints {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Joints::default())
  }
}

impl rosidl_runtime_rs::Message for Joints {
  type RmwMsg = super::msg::rmw::Joints;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        position: msg.position.into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        position: msg.position.as_slice().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      position: msg.position
          .into_iter()
          .collect(),
    }
  }
}


// Corresponds to champ_msgs__msg__Contacts

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Contacts {

    // This member is not documented.
    #[allow(missing_docs)]
    pub contacts: Vec<bool>,

}



impl Default for Contacts {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Contacts::default())
  }
}

impl rosidl_runtime_rs::Message for Contacts {
  type RmwMsg = super::msg::rmw::Contacts;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        contacts: msg.contacts.into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        contacts: msg.contacts.as_slice().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      contacts: msg.contacts
          .into_iter()
          .collect(),
    }
  }
}


// Corresponds to champ_msgs__msg__ContactsStamped

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ContactsStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub contacts: Vec<bool>,

}



impl Default for ContactsStamped {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::ContactsStamped::default())
  }
}

impl rosidl_runtime_rs::Message for ContactsStamped {
  type RmwMsg = super::msg::rmw::ContactsStamped;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Owned(msg.header)).into_owned(),
        contacts: msg.contacts.into(),
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        header: std_msgs::msg::Header::into_rmw_message(std::borrow::Cow::Borrowed(&msg.header)).into_owned(),
        contacts: msg.contacts.as_slice().into(),
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      header: std_msgs::msg::Header::from_rmw_message(msg.header),
      contacts: msg.contacts
          .into_iter()
          .collect(),
    }
  }
}


// Corresponds to champ_msgs__msg__Pose

// This struct is not documented.
#[allow(missing_docs)]

#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Pose {

    // This member is not documented.
    #[allow(missing_docs)]
    pub x: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub y: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub z: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub roll: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub pitch: f32,


    // This member is not documented.
    #[allow(missing_docs)]
    pub yaw: f32,

}



impl Default for Pose {
  fn default() -> Self {
    <Self as rosidl_runtime_rs::Message>::from_rmw_message(super::msg::rmw::Pose::default())
  }
}

impl rosidl_runtime_rs::Message for Pose {
  type RmwMsg = super::msg::rmw::Pose;

  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> {
    match msg_cow {
      std::borrow::Cow::Owned(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
        x: msg.x,
        y: msg.y,
        z: msg.z,
        roll: msg.roll,
        pitch: msg.pitch,
        yaw: msg.yaw,
      }),
      std::borrow::Cow::Borrowed(msg) => std::borrow::Cow::Owned(Self::RmwMsg {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      roll: msg.roll,
      pitch: msg.pitch,
      yaw: msg.yaw,
      })
    }
  }

  fn from_rmw_message(msg: Self::RmwMsg) -> Self {
    Self {
      x: msg.x,
      y: msg.y,
      z: msg.z,
      roll: msg.roll,
      pitch: msg.pitch,
      yaw: msg.yaw,
    }
  }
}


