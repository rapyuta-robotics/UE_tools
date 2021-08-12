// Copyright 2021 Rapyuta Robotics Co., Ltd.

#include "Srvs/ROS2{{data.NameCap}}Srv.h"

const rosidl_service_type_support_t* UROS2{{data.NameCap}}Srv::GetTypeSupport() const
{
    return ROSIDL_GET_SRV_TYPE_SUPPORT({{data.Group}}, srv, {{data.NameCap}});
}

void UROS2{{data.NameCap}}Srv::Init()
{
    {{data.Group}}__srv__{{data.NameCap}}_Request__init(&{{data.NameCap}}_req);
    {{data.Group}}__srv__{{data.NameCap}}_Response__init(&{{data.NameCap}}_res);
}

void UROS2{{data.NameCap}}Srv::Fini()
{
    {{data.Group}}__srv__{{data.NameCap}}_Request__fini(&{{data.NameCap}}_req);
    {{data.Group}}__srv__{{data.NameCap}}_Response__fini(&{{data.NameCap}}_res);
}

void UROS2{{data.NameCap}}Srv::SetInputs(const F{{data.StructName}} Input)
{
    Input.SetROS2({{data.NameCap}}_req.state);
}

void UROS2{{data.NameCap}}Srv::GetInputs(F{{data.StructName}}& Input) const
{
    Input.SetFromROS2({{data.NameCap}}_req.state);
}

void UROS2{{data.NameCap}}Srv::SetOutput(const F{{data.StructName}} Output)
{
    Output.SetROS2({{data.NameCap}}_res.state);
}

void UROS2{{data.NameCap}}Srv::GetOutput(F{{data.StructName}}& Output) const
{
    Output.SetFromROS2({{data.NameCap}}_res.state);
}

void* UROS2{{data.NameCap}}Srv::GetRequest()
{
    return &{{data.NameCap}}_req;
}

void* UROS2{{data.NameCap}}Srv::GetResponse()
{
    return &{{data.NameCap}}_res;
}

const FString UROS2{{data.NameCap}}Srv::SrvRequestToString() const
{
    /* TODO: Fill here */
	checkNoEntry();
    return FString();
}

const FString UROS2{{data.NameCap}}Srv::SrvResponseToString() const
{
    /* TODO: Fill here */
	checkNoEntry();
    return FString();
}
