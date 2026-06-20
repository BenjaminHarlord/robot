#[cfg(feature = "serde")]
use serde::{Deserialize, Serialize};


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Velocities() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__Velocities__init(msg: *mut Velocities) -> bool;
    fn champ_msgs__msg__Velocities__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Velocities>, size: usize) -> bool;
    fn champ_msgs__msg__Velocities__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Velocities>);
    fn champ_msgs__msg__Velocities__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Velocities>, out_seq: *mut rosidl_runtime_rs::Sequence<Velocities>) -> bool;
}

// Corresponds to champ_msgs__msg__Velocities
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
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
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__Velocities__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__Velocities__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Velocities {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Velocities__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Velocities__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Velocities__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Velocities {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Velocities where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/Velocities";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Velocities() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__PID() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__PID__init(msg: *mut PID) -> bool;
    fn champ_msgs__msg__PID__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<PID>, size: usize) -> bool;
    fn champ_msgs__msg__PID__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<PID>);
    fn champ_msgs__msg__PID__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<PID>, out_seq: *mut rosidl_runtime_rs::Sequence<PID>) -> bool;
}

// Corresponds to champ_msgs__msg__PID
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
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
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__PID__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__PID__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for PID {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__PID__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__PID__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__PID__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for PID {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for PID where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/PID";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__PID() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Imu() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__Imu__init(msg: *mut Imu) -> bool;
    fn champ_msgs__msg__Imu__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Imu>, size: usize) -> bool;
    fn champ_msgs__msg__Imu__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Imu>);
    fn champ_msgs__msg__Imu__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Imu>, out_seq: *mut rosidl_runtime_rs::Sequence<Imu>) -> bool;
}

// Corresponds to champ_msgs__msg__Imu
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Imu {

    // This member is not documented.
    #[allow(missing_docs)]
    pub orientation: geometry_msgs::msg::rmw::Quaternion,


    // This member is not documented.
    #[allow(missing_docs)]
    pub linear_acceleration: geometry_msgs::msg::rmw::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub angular_velocity: geometry_msgs::msg::rmw::Vector3,


    // This member is not documented.
    #[allow(missing_docs)]
    pub magnetic_field: geometry_msgs::msg::rmw::Vector3,

}



impl Default for Imu {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__Imu__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__Imu__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Imu {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Imu__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Imu__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Imu__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Imu {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Imu where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/Imu";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Imu() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Point() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__Point__init(msg: *mut Point) -> bool;
    fn champ_msgs__msg__Point__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Point>, size: usize) -> bool;
    fn champ_msgs__msg__Point__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Point>);
    fn champ_msgs__msg__Point__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Point>, out_seq: *mut rosidl_runtime_rs::Sequence<Point>) -> bool;
}

// Corresponds to champ_msgs__msg__Point
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
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
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__Point__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__Point__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Point {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Point__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Point__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Point__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Point {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Point where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/Point";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Point() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__PointArray() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__PointArray__init(msg: *mut PointArray) -> bool;
    fn champ_msgs__msg__PointArray__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<PointArray>, size: usize) -> bool;
    fn champ_msgs__msg__PointArray__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<PointArray>);
    fn champ_msgs__msg__PointArray__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<PointArray>, out_seq: *mut rosidl_runtime_rs::Sequence<PointArray>) -> bool;
}

// Corresponds to champ_msgs__msg__PointArray
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct PointArray {

    // This member is not documented.
    #[allow(missing_docs)]
    pub lf: super::super::msg::rmw::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rf: super::super::msg::rmw::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub lh: super::super::msg::rmw::Point,


    // This member is not documented.
    #[allow(missing_docs)]
    pub rh: super::super::msg::rmw::Point,

}



impl Default for PointArray {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__PointArray__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__PointArray__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for PointArray {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__PointArray__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__PointArray__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__PointArray__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for PointArray {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for PointArray where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/PointArray";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__PointArray() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Joints() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__Joints__init(msg: *mut Joints) -> bool;
    fn champ_msgs__msg__Joints__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Joints>, size: usize) -> bool;
    fn champ_msgs__msg__Joints__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Joints>);
    fn champ_msgs__msg__Joints__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Joints>, out_seq: *mut rosidl_runtime_rs::Sequence<Joints>) -> bool;
}

// Corresponds to champ_msgs__msg__Joints
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Joints {

    // This member is not documented.
    #[allow(missing_docs)]
    pub position: rosidl_runtime_rs::Sequence<f32>,

}



impl Default for Joints {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__Joints__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__Joints__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Joints {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Joints__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Joints__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Joints__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Joints {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Joints where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/Joints";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Joints() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Contacts() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__Contacts__init(msg: *mut Contacts) -> bool;
    fn champ_msgs__msg__Contacts__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Contacts>, size: usize) -> bool;
    fn champ_msgs__msg__Contacts__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Contacts>);
    fn champ_msgs__msg__Contacts__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Contacts>, out_seq: *mut rosidl_runtime_rs::Sequence<Contacts>) -> bool;
}

// Corresponds to champ_msgs__msg__Contacts
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct Contacts {

    // This member is not documented.
    #[allow(missing_docs)]
    pub contacts: rosidl_runtime_rs::Sequence<bool>,

}



impl Default for Contacts {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__Contacts__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__Contacts__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Contacts {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Contacts__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Contacts__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Contacts__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Contacts {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Contacts where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/Contacts";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Contacts() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__ContactsStamped() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__ContactsStamped__init(msg: *mut ContactsStamped) -> bool;
    fn champ_msgs__msg__ContactsStamped__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<ContactsStamped>, size: usize) -> bool;
    fn champ_msgs__msg__ContactsStamped__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<ContactsStamped>);
    fn champ_msgs__msg__ContactsStamped__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<ContactsStamped>, out_seq: *mut rosidl_runtime_rs::Sequence<ContactsStamped>) -> bool;
}

// Corresponds to champ_msgs__msg__ContactsStamped
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
#[derive(Clone, Debug, PartialEq, PartialOrd)]
pub struct ContactsStamped {

    // This member is not documented.
    #[allow(missing_docs)]
    pub header: std_msgs::msg::rmw::Header,


    // This member is not documented.
    #[allow(missing_docs)]
    pub contacts: rosidl_runtime_rs::Sequence<bool>,

}



impl Default for ContactsStamped {
  fn default() -> Self {
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__ContactsStamped__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__ContactsStamped__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for ContactsStamped {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__ContactsStamped__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__ContactsStamped__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__ContactsStamped__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for ContactsStamped {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for ContactsStamped where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/ContactsStamped";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__ContactsStamped() }
  }
}


#[link(name = "champ_msgs__rosidl_typesupport_c")]
extern "C" {
    fn rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Pose() -> *const std::ffi::c_void;
}

#[link(name = "champ_msgs__rosidl_generator_c")]
extern "C" {
    fn champ_msgs__msg__Pose__init(msg: *mut Pose) -> bool;
    fn champ_msgs__msg__Pose__Sequence__init(seq: *mut rosidl_runtime_rs::Sequence<Pose>, size: usize) -> bool;
    fn champ_msgs__msg__Pose__Sequence__fini(seq: *mut rosidl_runtime_rs::Sequence<Pose>);
    fn champ_msgs__msg__Pose__Sequence__copy(in_seq: &rosidl_runtime_rs::Sequence<Pose>, out_seq: *mut rosidl_runtime_rs::Sequence<Pose>) -> bool;
}

// Corresponds to champ_msgs__msg__Pose
#[cfg_attr(feature = "serde", derive(Deserialize, Serialize))]


// This struct is not documented.
#[allow(missing_docs)]

#[repr(C)]
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
    unsafe {
      let mut msg = std::mem::zeroed();
      if !champ_msgs__msg__Pose__init(&mut msg as *mut _) {
        panic!("Call to champ_msgs__msg__Pose__init() failed");
      }
      msg
    }
  }
}

impl rosidl_runtime_rs::SequenceAlloc for Pose {
  fn sequence_init(seq: &mut rosidl_runtime_rs::Sequence<Self>, size: usize) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Pose__Sequence__init(seq as *mut _, size) }
  }
  fn sequence_fini(seq: &mut rosidl_runtime_rs::Sequence<Self>) {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Pose__Sequence__fini(seq as *mut _) }
  }
  fn sequence_copy(in_seq: &rosidl_runtime_rs::Sequence<Self>, out_seq: &mut rosidl_runtime_rs::Sequence<Self>) -> bool {
    // SAFETY: This is safe since the pointer is guaranteed to be valid/initialized.
    unsafe { champ_msgs__msg__Pose__Sequence__copy(in_seq, out_seq as *mut _) }
  }
}

impl rosidl_runtime_rs::Message for Pose {
  type RmwMsg = Self;
  fn into_rmw_message(msg_cow: std::borrow::Cow<'_, Self>) -> std::borrow::Cow<'_, Self::RmwMsg> { msg_cow }
  fn from_rmw_message(msg: Self::RmwMsg) -> Self { msg }
}

impl rosidl_runtime_rs::RmwMessage for Pose where Self: Sized {
  const TYPE_NAME: &'static str = "champ_msgs/msg/Pose";
  fn get_type_support() -> *const std::ffi::c_void {
    // SAFETY: No preconditions for this function.
    unsafe { rosidl_typesupport_c__get_message_type_support_handle__champ_msgs__msg__Pose() }
  }
}


