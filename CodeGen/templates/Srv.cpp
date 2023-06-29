// Copyright 2023 Rapyuta Robotics Co., Ltd.
// This code has been autogenerated from {{data.Filename}} - do not modify

#include "Srvs/ROS2{{data.UEName}}.h"


{{data.ReqConstantsDef}}
{{data.ResConstantsDef}}

const rosidl_service_type_support_t* UROS2{{data.UEName}}Srv::GetTypeSupport() const
{
    return ROSIDL_GET_SRV_TYPE_SUPPORT({{data.Group}}, srv, {{data.NameCap}});
}

void UROS2{{data.UEName}}Srv::Init()
{
    {{data.Group}}__srv__{{data.NameCap}}_Request__init(&{{data.NameCap}}_req);
    {{data.Group}}__srv__{{data.NameCap}}_Response__init(&{{data.NameCap}}_res);
}

void UROS2{{data.UEName}}Srv::Fini()
{
    {{data.Group}}__srv__{{data.NameCap}}_Request__fini(&{{data.NameCap}}_req);
    {{data.Group}}__srv__{{data.NameCap}}_Response__fini(&{{data.NameCap}}_res);
}

void UROS2{{data.UEName}}Srv::SetRequest(const FROS{{data.UEName}}Req& Request)
{
    Request.SetROS2({{data.NameCap}}_req);
}

void UROS2{{data.UEName}}Srv::GetRequest(FROS{{data.UEName}}Req& Request) const
{
    Request.SetFromROS2({{data.NameCap}}_req);
}

void UROS2{{data.UEName}}Srv::SetResponse(const FROS{{data.UEName}}Res& Response)
{
    Response.SetROS2({{data.NameCap}}_res);
}

void UROS2{{data.UEName}}Srv::GetResponse(FROS{{data.UEName}}Res& Response) const
{
    Response.SetFromROS2({{data.NameCap}}_res);
}

void* UROS2{{data.UEName}}Srv::GetRequest()
{
    return &{{data.NameCap}}_req;
}

void* UROS2{{data.UEName}}Srv::GetResponse()
{
    return &{{data.NameCap}}_res;
}

FString UROS2{{data.UEName}}Srv::SrvRequestToString() const
{
    /* TODO: Fill here */
	checkNoEntry();
    return FString();
}

FString UROS2{{data.UEName}}Srv::SrvResponseToString() const
{
    /* TODO: Fill here */
	checkNoEntry();
    return FString();
}
