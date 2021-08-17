// Copyright 2021 Rapyuta Robotics Co., Ltd.

#include "Actions/ROS2{{data.NameCap}}Action.h"

const rosidl_action_type_support_t* UROS2{{data.NameCap}}Action::GetTypeSupport() const
{
    return ROSIDL_GET_ACTION_TYPE_SUPPORT({{data.Group}}, {{data.NameCap}});
}

void UROS2{{data.NameCap}}Action::Init()
{
    Super::Init();
    {{data.Group}}__action__{{data.NameCap}}_SendGoal_Request__init(&{{data.NameCap}}_goal_request);
    {{data.Group}}__action__{{data.NameCap}}_SendGoal_Response__init(&{{data.NameCap}}_goal_response);
    {{data.Group}}__action__{{data.NameCap}}_GetResult_Request__init(&{{data.NameCap}}_result_request);
    {{data.Group}}__action__{{data.NameCap}}_GetResult_Response__init(&{{data.NameCap}}_result_response);
    {{data.Group}}__action__{{data.NameCap}}_FeedbackMessage__init(&{{data.NameCap}}_feedback_message);
}

void UROS2{{data.NameCap}}Action::Fini()
{
    {{data.Group}}__action__{{data.NameCap}}_SendGoal_Request__fini(&{{data.NameCap}}_goal_request);
    {{data.Group}}__action__{{data.NameCap}}_SendGoal_Response__fini(&{{data.NameCap}}_goal_response);
    {{data.Group}}__action__{{data.NameCap}}_GetResult_Request__fini(&{{data.NameCap}}_result_request);
    {{data.Group}}__action__{{data.NameCap}}_GetResult_Response__fini(&{{data.NameCap}}_result_response);
    {{data.Group}}__action__{{data.NameCap}}_FeedbackMessage__fini(&{{data.NameCap}}_feedback_message);
    Super::Fini();
}

void UROS2{{data.NameCap}}Action::SetGoalRequest(const F{{data.StructName}}_SendGoal_Request Goal)
{
    Goal.SetROS2({{data.NameCap}}_goal_request);
}

void UROS2{{data.NameCap}}Action::GetGoalRequest(F{{data.StructName}}_SendGoal_Request& Goal) const
{
    Goal.SetFromROS2({{data.NameCap}}_goal_request);
}

void UROS2{{data.NameCap}}Action::SetGoalResponse(const F{{data.StructName}}_SendGoal_Response Goal)
{
    Goal.SetROS2({{data.NameCap}}_goal_response);
}

void UROS2{{data.NameCap}}Action::GetGoalResponse(F{{data.StructName}}_SendGoal_Response& Goal) const
{
    Goal.SetFromROS2({{data.NameCap}}_goal_response);
}

void UROS2{{data.NameCap}}Action::SetResultRequest(const F{{data.StructName}}_GetResult_Request Result)
{
    Result.SetROS2({{data.NameCap}}_result_request);
}

void UROS2{{data.NameCap}}Action::GetResultRequest(F{{data.StructName}}_GetResult_Request& Result) const
{
    Result.SetFromROS2({{data.NameCap}}_result_request);
}

void UROS2{{data.NameCap}}Action::SetResultResponse(const F{{data.StructName}}_GetResult_Response Result)
{
    Result.SetROS2({{data.NameCap}}_result_response);
}

void UROS2{{data.NameCap}}Action::GetResultResponse(F{{data.StructName}}_GetResult_Response& Result) const
{
    Result.SetFromROS2({{data.NameCap}}_result_response);
}


void UROS2{{data.NameCap}}Action::SetFeedback(const F{{data.StructName}}_FeedbackMessage Feedback)
{
    Feedback.SetROS2({{data.NameCap}}_feedback_message);
}

void UROS2{{data.NameCap}}Action::GetFeedback(F{{data.StructName}}_FeedbackMessage& Feedback) const
{
    Feedback.SetFromROS2({{data.NameCap}}_feedback_message);
}


void* UROS2{{data.NameCap}}Action::GetGoalRequest()
{
    return &{{data.NameCap}}_goal_request;
}

void* UROS2{{data.NameCap}}Action::GetGoalResponse()
{
    return &{{data.NameCap}}_goal_response;
}

void* UROS2{{data.NameCap}}Action::GetResultRequest()
{
    return &{{data.NameCap}}_result_request;
}

void* UROS2{{data.NameCap}}Action::GetResultResponse()
{
    return &{{data.NameCap}}_result_response;
}

void* UROS2{{data.NameCap}}Action::GetFeedbackMessage()
{
    return &{{data.NameCap}}_feedback_message;
}
