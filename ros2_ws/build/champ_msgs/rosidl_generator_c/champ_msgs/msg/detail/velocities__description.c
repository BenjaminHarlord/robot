// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from champ_msgs:msg/Velocities.idl
// generated code does not contain a copyright notice

#include "champ_msgs/msg/detail/velocities__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_champ_msgs
const rosidl_type_hash_t *
champ_msgs__msg__Velocities__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x9b, 0x3e, 0x29, 0x9b, 0x5a, 0x80, 0xc3, 0xf7,
      0x59, 0x2b, 0xcc, 0xb4, 0x67, 0x71, 0xa8, 0x4c,
      0xe6, 0xb1, 0x0c, 0x09, 0x26, 0x89, 0x83, 0x7b,
      0x4c, 0x35, 0xc3, 0xf5, 0xc4, 0xb5, 0x45, 0xc8,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char champ_msgs__msg__Velocities__TYPE_NAME[] = "champ_msgs/msg/Velocities";

// Define type names, field names, and default values
static char champ_msgs__msg__Velocities__FIELD_NAME__linear_x[] = "linear_x";
static char champ_msgs__msg__Velocities__FIELD_NAME__linear_y[] = "linear_y";
static char champ_msgs__msg__Velocities__FIELD_NAME__angular_z[] = "angular_z";

static rosidl_runtime_c__type_description__Field champ_msgs__msg__Velocities__FIELDS[] = {
  {
    {champ_msgs__msg__Velocities__FIELD_NAME__linear_x, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Velocities__FIELD_NAME__linear_y, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Velocities__FIELD_NAME__angular_z, 9, 9},
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
champ_msgs__msg__Velocities__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {champ_msgs__msg__Velocities__TYPE_NAME, 25, 25},
      {champ_msgs__msg__Velocities__FIELDS, 3, 3},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "\n"
  "float32 linear_x\n"
  "float32 linear_y\n"
  "float32 angular_z";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
champ_msgs__msg__Velocities__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {champ_msgs__msg__Velocities__TYPE_NAME, 25, 25},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 53, 53},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
champ_msgs__msg__Velocities__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *champ_msgs__msg__Velocities__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
