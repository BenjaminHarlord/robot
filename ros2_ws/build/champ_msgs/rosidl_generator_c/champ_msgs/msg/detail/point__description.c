// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from champ_msgs:msg/Point.idl
// generated code does not contain a copyright notice

#include "champ_msgs/msg/detail/point__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_champ_msgs
const rosidl_type_hash_t *
champ_msgs__msg__Point__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xe5, 0x1d, 0x61, 0xa1, 0xf4, 0x8c, 0x57, 0x40,
      0x26, 0xa4, 0xc7, 0x94, 0xd7, 0xf1, 0xe2, 0x37,
      0x71, 0x71, 0xce, 0xeb, 0xa1, 0xf8, 0x8a, 0x2e,
      0x59, 0xd0, 0x35, 0x92, 0xda, 0x7c, 0xeb, 0x01,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char champ_msgs__msg__Point__TYPE_NAME[] = "champ_msgs/msg/Point";

// Define type names, field names, and default values
static char champ_msgs__msg__Point__FIELD_NAME__x[] = "x";
static char champ_msgs__msg__Point__FIELD_NAME__y[] = "y";
static char champ_msgs__msg__Point__FIELD_NAME__z[] = "z";

static rosidl_runtime_c__type_description__Field champ_msgs__msg__Point__FIELDS[] = {
  {
    {champ_msgs__msg__Point__FIELD_NAME__x, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Point__FIELD_NAME__y, 1, 1},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_FLOAT,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__Point__FIELD_NAME__z, 1, 1},
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
champ_msgs__msg__Point__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {champ_msgs__msg__Point__TYPE_NAME, 20, 20},
      {champ_msgs__msg__Point__FIELDS, 3, 3},
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
  "float32 z";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
champ_msgs__msg__Point__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {champ_msgs__msg__Point__TYPE_NAME, 20, 20},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 29, 29},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
champ_msgs__msg__Point__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *champ_msgs__msg__Point__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
