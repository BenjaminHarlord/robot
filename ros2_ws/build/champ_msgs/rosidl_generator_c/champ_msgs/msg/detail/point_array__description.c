// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from champ_msgs:msg/PointArray.idl
// generated code does not contain a copyright notice

#include "champ_msgs/msg/detail/point_array__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_champ_msgs
const rosidl_type_hash_t *
champ_msgs__msg__PointArray__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0xf0, 0xc7, 0x28, 0x4c, 0x08, 0x7c, 0x4c, 0xa5,
      0x4d, 0xf4, 0x65, 0x90, 0xd8, 0xcc, 0xc7, 0x5f,
      0x13, 0x9c, 0x12, 0xf6, 0xd4, 0x37, 0xe6, 0x34,
      0xeb, 0xf8, 0x06, 0xcb, 0xe3, 0xf0, 0x27, 0xb7,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types
#include "champ_msgs/msg/detail/point__functions.h"

// Hashes for external referenced types
#ifndef NDEBUG
static const rosidl_type_hash_t champ_msgs__msg__Point__EXPECTED_HASH = {1, {
    0xe5, 0x1d, 0x61, 0xa1, 0xf4, 0x8c, 0x57, 0x40,
    0x26, 0xa4, 0xc7, 0x94, 0xd7, 0xf1, 0xe2, 0x37,
    0x71, 0x71, 0xce, 0xeb, 0xa1, 0xf8, 0x8a, 0x2e,
    0x59, 0xd0, 0x35, 0x92, 0xda, 0x7c, 0xeb, 0x01,
  }};
#endif

static char champ_msgs__msg__PointArray__TYPE_NAME[] = "champ_msgs/msg/PointArray";
static char champ_msgs__msg__Point__TYPE_NAME[] = "champ_msgs/msg/Point";

// Define type names, field names, and default values
static char champ_msgs__msg__PointArray__FIELD_NAME__lf[] = "lf";
static char champ_msgs__msg__PointArray__FIELD_NAME__rf[] = "rf";
static char champ_msgs__msg__PointArray__FIELD_NAME__lh[] = "lh";
static char champ_msgs__msg__PointArray__FIELD_NAME__rh[] = "rh";

static rosidl_runtime_c__type_description__Field champ_msgs__msg__PointArray__FIELDS[] = {
  {
    {champ_msgs__msg__PointArray__FIELD_NAME__lf, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {champ_msgs__msg__Point__TYPE_NAME, 20, 20},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__PointArray__FIELD_NAME__rf, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {champ_msgs__msg__Point__TYPE_NAME, 20, 20},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__PointArray__FIELD_NAME__lh, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {champ_msgs__msg__Point__TYPE_NAME, 20, 20},
    },
    {NULL, 0, 0},
  },
  {
    {champ_msgs__msg__PointArray__FIELD_NAME__rh, 2, 2},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_NESTED_TYPE,
      0,
      0,
      {champ_msgs__msg__Point__TYPE_NAME, 20, 20},
    },
    {NULL, 0, 0},
  },
};

static rosidl_runtime_c__type_description__IndividualTypeDescription champ_msgs__msg__PointArray__REFERENCED_TYPE_DESCRIPTIONS[] = {
  {
    {champ_msgs__msg__Point__TYPE_NAME, 20, 20},
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
champ_msgs__msg__PointArray__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {champ_msgs__msg__PointArray__TYPE_NAME, 25, 25},
      {champ_msgs__msg__PointArray__FIELDS, 4, 4},
    },
    {champ_msgs__msg__PointArray__REFERENCED_TYPE_DESCRIPTIONS, 1, 1},
  };
  if (!constructed) {
    assert(0 == memcmp(&champ_msgs__msg__Point__EXPECTED_HASH, champ_msgs__msg__Point__get_type_hash(NULL), sizeof(rosidl_type_hash_t)));
    description.referenced_type_descriptions.data[0].fields = champ_msgs__msg__Point__get_type_description(NULL)->type_description.fields;
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "champ_msgs/Point lf\n"
  "champ_msgs/Point rf\n"
  "champ_msgs/Point lh\n"
  "champ_msgs/Point rh";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
champ_msgs__msg__PointArray__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {champ_msgs__msg__PointArray__TYPE_NAME, 25, 25},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 79, 79},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
champ_msgs__msg__PointArray__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[2];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 2, 2};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *champ_msgs__msg__PointArray__get_individual_type_description_source(NULL),
    sources[1] = *champ_msgs__msg__Point__get_individual_type_description_source(NULL);
    constructed = true;
  }
  return &source_sequence;
}
