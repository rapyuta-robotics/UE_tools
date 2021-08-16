// Copyright 2021 Rapyuta Robotics Co., Ltd.

#pragma once

#include "CoreMinimal.h"

#include "{{data.Group}}/action/{{data.Name}}.h"
#include "action_msgs/srv/cancel_goal.h"

#include "Actions/ROS2GenericAction.h"
#include "rclcUtilities.h"

#include "ROS2{{data.NameCap}}Action.generated.h"

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_SendGoal_Request
{
	GENERATED_BODY()

public:
	{{data.GoalReqTypes}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}}_SendGoal_Request data)
	{
    	{{data.GoalReqSetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}_SendGoal_Request& data) const
	{
    	{{data.GoalReqSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_SendGoal_Response
{
	GENERATED_BODY()

public:
	{{data.GoalResTypes}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}}_SendGoal_Response data)
	{
    	{{data.GoalResSetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}_SendGoal_Response& data) const
	{
    	{{data.GoalResSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_GetResult_Request
{
	GENERATED_BODY()

public:
	{{data.ResultReqTypes}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}}_GetResult_Request data)
	{
    	{{data.ResultReqSetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}_GetResult_Request& data) const
	{
    	{{data.ResultReqSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_GetResult_Response
{
	GENERATED_BODY()

public:
	{{data.ResultResTypes}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}}_GetResult_Response data)
	{
    	{{data.ResultResSetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}_GetResult_Response& data) const
	{
    	{{data.ResultResSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_FeedbackMessage
{
	GENERATED_BODY()

public:
	{{data.FeedbackTypes}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}}_FeedbackMessage data)
	{
    	{{data.FeedbackSetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}_FeedbackMessage& data) const
	{
    	{{data.FeedbackSetROS2}}
	}
};

UCLASS()
class RCLUE_API UROS2{{data.NameCap}}Action : public UROS2GenericAction
{
	GENERATED_BODY()
	
public:
	virtual void Init() override;

	virtual void Fini() override;

	virtual const rosidl_action_type_support_t* GetTypeSupport() const override;
	
  	UFUNCTION(BlueprintCallable)
	void SetGoal(const F{{data.StructName}}_SendGoal_Request Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoal(F{{data.StructName}}_SendGoal_Request& Goal) const;

  	UFUNCTION(BlueprintCallable)
	void SetResult(const F{{data.StructName}}_GetResult_Request Result);

  	UFUNCTION(BlueprintCallable)
	void GetResult(F{{data.StructName}}_GetResult_Request& Result) const;

	// TODO these are for a future refactoring, as it requires to adapt the rest of the codes	
  	UFUNCTION(BlueprintCallable)
	void SetGoalRequest(const F{{data.StructName}}_SendGoal_Request Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalRequest(F{{data.StructName}}_SendGoal_Request& Goal) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetGoalResponse(const F{{data.StructName}}_SendGoal_Response Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalResponse(F{{data.StructName}}_SendGoal_Response& Goal) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetGoalRequest(const F{{data.StructName}}_GetResult_Request Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalRequest(F{{data.StructName}}_GetResult_Request& Goal) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetGoalResponse(const F{{data.StructName}}_GetResult_Response Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalResponse(F{{data.StructName}}_GetResult_Response& Goal) const;



  	UFUNCTION(BlueprintCallable)
	void SetFeedback(const F{{data.StructName}}_FeedbackMessage Feedback);

  	UFUNCTION(BlueprintCallable)
	void GetFeedback(F{{data.StructName}}_FeedbackMessage& Feedback) const;
	
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
