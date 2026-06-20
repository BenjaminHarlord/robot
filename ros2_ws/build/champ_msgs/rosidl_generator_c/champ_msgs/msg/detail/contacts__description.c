// generated from rosidl_generator_c/resource/idl__description.c.em
// with input from champ_msgs:msg/Contacts.idl
// generated code does not contain a copyright notice

#include "champ_msgs/msg/detail/contacts__functions.h"

ROSIDL_GENERATOR_C_PUBLIC_champ_msgs
const rosidl_type_hash_t *
champ_msgs__msg__Contacts__get_type_hash(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_type_hash_t hash = {1, {
      0x89, 0x93, 0x06, 0x6f, 0xb6, 0x72, 0x89, 0x0a,
      0x53, 0xea, 0xa2, 0x37, 0x1e, 0x64, 0xc7, 0x1b,
      0x9f, 0xb9, 0x40, 0xad, 0x98, 0x35, 0x9a, 0x40,
      0x8f, 0xa3, 0x61, 0x22, 0x07, 0x1d, 0x1a, 0x19,
    }};
  return &hash;
}

#include <assert.h>
#include <string.h>

// Include directives for referenced types

// Hashes for external referenced types
#ifndef NDEBUG
#endif

static char champ_msgs__msg__Contacts__TYPE_NAME[] = "champ_msgs/msg/Contacts";

// Define type names, field names, and default values
static char champ_msgs__msg__Contacts__FIELD_NAME__contacts[] = "contacts";

static rosidl_runtime_c__type_description__Field champ_msgs__msg__Contacts__FIELDS[] = {
  {
    {champ_msgs__msg__Contacts__FIELD_NAME__contacts, 8, 8},
    {
      rosidl_runtime_c__type_description__FieldType__FIELD_TYPE_BOOLEAN_UNBOUNDED_SEQUENCE,
      0,
      0,
      {NULL, 0, 0},
    },
    {NULL, 0, 0},
  },
};

const rosidl_runtime_c__type_description__TypeDescription *
champ_msgs__msg__Contacts__get_type_description(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static bool constructed = false;
  static const rosidl_runtime_c__type_description__TypeDescription description = {
    {
      {champ_msgs__msg__Contacts__TYPE_NAME, 23, 23},
      {champ_msgs__msg__Contacts__FIELDS, 1, 1},
    },
    {NULL, 0, 0},
  };
  if (!constructed) {
    constructed = true;
  }
  return &description;
}

static char toplevel_type_raw_source[] =
  "bool[] contacts";

static char msg_encoding[] = "msg";

// Define all individual source functions

const rosidl_runtime_c__type_description__TypeSource *
champ_msgs__msg__Contacts__get_individual_type_description_source(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static const rosidl_runtime_c__type_description__TypeSource source = {
    {champ_msgs__msg__Contacts__TYPE_NAME, 23, 23},
    {msg_encoding, 3, 3},
    {toplevel_type_raw_source, 15, 15},
  };
  return &source;
}

const rosidl_runtime_c__type_description__TypeSource__Sequence *
champ_msgs__msg__Contacts__get_type_description_sources(
  const rosidl_message_type_support_t * type_support)
{
  (void)type_support;
  static rosidl_runtime_c__type_description__TypeSource sources[1];
  static const rosidl_runtime_c__type_description__TypeSource__Sequence source_sequence = {sources, 1, 1};
  static bool constructed = false;
  if (!constructed) {
    sources[0] = *champ_msgs__msg__Contacts__get_individual_type_description_source(NULL),
    constructed = true;
  }
  return &source_sequence;
}
