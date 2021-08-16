// Copyright 2021 Rapyuta Robotics Co., Ltd.

#include "Msgs/ROS2{{data.NameCap}}Msg.h"

#include "Kismet/GameplayStatics.h"

void UROS2{{data.NameCap}}Msg::Init()
{
	{{data.Group}}__msg__{{data.NameCap}}__init(&{{data.Name}}_msg);
}

void UROS2{{data.NameCap}}Msg::Fini()
{
	{{data.Group}}__msg__{{data.NameCap}}__fini(&{{data.Name}}_msg);
}

const rosidl_message_type_support_t* UROS2{{data.NameCap}}Msg::GetTypeSupport() const
{
	return ROSIDL_GET_MSG_TYPE_SUPPORT({{data.Group}}, msg, {{data.NameCap}});
}

void UROS2{{data.NameCap}}Msg::Update(const F{{data.StructName}} Inputs)
{
    Inputs.SetROS2({{data.Name}}_msg);
}

void UROS2{{data.NameCap}}Msg::SetMsg(const F{{data.StructName}} Inputs)
{
    Inputs.SetROS2({{data.Name}}_msg);
}

void UROS2{{data.NameCap}}Msg::GetMsg(const F{{data.StructName}}& Outputs)
{
    Inputs.SetFromROS2({{data.Name}}_msg);
}

void* UROS2{{data.NameCap}}Msg::Get()
{
	return &{{data.Name}}_msg;
}

FString UROS2{{data.NameCap}}Msg::MsgToString() const
{
    /* TODO: Fill here */
	checkNoEntry();
	return FString();
}