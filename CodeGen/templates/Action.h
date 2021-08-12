// Copyright 2021 Rapyuta Robotics Co., Ltd.

#pragma once

#include "CoreMinimal.h"

#include "{{data.Group}}/action/{{data.Name}}.h"
#include "action_msgs/srv/cancel_goal.h"

#include "Actions/ROS2GenericAction.h"
#include "rclcUtilities.h"

#include "ROS2{{data.NameCap}}Action.generated.h"

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}
{
	GENERATED_BODY()

public:
	{{data.Types}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}} data)
	{
    	/* TODO: Fill here */
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}& data) const
	{
    	/* TODO: Fill here */
	}
}

UCLASS()
class RCLUE_API UROS2{{data.NameCap}}Action : public UROS2GenericAction
{
	GENERATED_BODY()
	
public:
	virtual void Init() override;

	virtual void Fini() override;

	virtual const rosidl_action_type_support_t* GetTypeSupport() const override;
	
  	UFUNCTION(BlueprintCallable)
	void SetGoal(const F{{data.StructName}} Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoal(F{{data.StructName}}& Goal) const;

  	UFUNCTION(BlueprintCallable)
	void SetResult(const F{{data.StructName}} Result);

  	UFUNCTION(BlueprintCallable)
	void GetResult(F{{data.StructName}}& Result) const;

  	UFUNCTION(BlueprintCallable)
	void SetFeedback(const F{{data.StructName}} Feedback);

  	UFUNCTION(BlueprintCallable)
	void GetFeedback(F{{data.StructName}}& Feedback) const;
	
	virtual void* GetGoalRequest() override;
	virtual void* GetGoalResponse() override;
	virtual void* GetResultRequest() override;
	virtual void* GetResultResponse() override;
	virtual void* GetFeedbackMessage() override;

private:
	{{data.Group}}__action__{{data.NameCap}}_SendGoal_Request {{data.NameCap}}_goal_request;
	{{data.Group}}__action__{{data.NameCap}}_SendGoal_Response {{data.NameCap}}_goal_response;
	{{data.Group}}__action__{{data.NameCap}}_GetResult_Request {{data.NameCap}}_result_request;
	{{data.Group}}__action__{{data.NameCap}}_GetResult_Response {{data.NameCap}}_result_response;
	{{data.Group}}__action__{{data.NameCap}}_FeedbackMessage {{data.NameCap}}_feedback_message;
};
