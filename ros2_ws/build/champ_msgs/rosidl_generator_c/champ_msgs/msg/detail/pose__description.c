// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from champ_msgs:msg/Pose.idl
// generated code does not contain a copyright notice

#include "champ_msgs/msg/detail/pose__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_champ_msgs
const rosidl_type_hash_t *
champ_msgs__msg__Pose__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xe3, 0x6e, 0x74, 0x94, 0x91, 0x9d, 0x07, 0x81,
      0x02, 0xbb, 0xd3, 0x1e, 0xad, 0x0c, 0x66, 0x8e,
      0x80, 0x9b, 0x98, 0x09, 0xd6, 0x88, 0x26, 0x66,
      0xc7, 0x0b, 0x02, 0xd9, 0x50, 0x97, 0xc4, 0x5a,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char champ_msgs__msg__Pose__TYPE_NAME[] = "champ_msgs/msg/Pose";

// Define type names, field names, and default values
static char champ_msgs__msg__Pose__FIELD_NAME__x[] = "x";
static char champ_msgs__msg__Pose__FIELD_NAME__y[] = "y";
static char champ_msgs__msg__Pose__FIELD_NAME__z[] = "z";
static char champ_msgs__msg__Pose__FIELD_NAME__roll[] = "roll";
static char champ_msgs__msg__Pose__FIELD_NAME__pitch[] = "pitch";
static char champ_msgs__msg__Pose__FIELD_NAME__yaw[] = "yaw";

static rosidl_runtime_c__type_description__Field champ_msgs__msg__Pose__FIELDS[] = {
  {
    {champ_msgs__msg__Pose__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Pose__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Pose__FIELD_NAME__z, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Pose__FIELD_NAME__roll, 4, 4},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Pose__FIELD_NAME__pitch, 5, 5},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Pose__FIELD_NAME__yaw, 3, 3},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
champ_msgs__msg__Pose__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {champ_msgs__msg__Pose__TYPE_NAME, 19, 19},
      {champ_msgs__msg__Pose__FIELDS, 6, 6},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "float32 x\n"
  "float32 y\n"
  "float32 z\n"
  "float32 roll\n"
  "float32 pitch\n"
  "float32 yaw";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
champ_msgs__msg__Pose__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {champ_msgs__msg__Pose__TYPE_NAME, 19, 19},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 69, 69},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
champ_msgs__msg__Pose__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *champ_msgs__msg__Pose__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
