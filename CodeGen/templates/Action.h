// Copyright 2021 Rapyuta Robotics Co., Ltd.

#pragma once

#include "CoreMinimal.h"

#include "unique_identifier_msgs/msg/uuid.h"
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
  	TArray<uint, TFixedAllocator<16>> goal_id;
	{{data.GoalTypes}}

	void SetFromROS2({{data.Group}}__action__{{data.NameCap}}_SendGoal_Request data)
	{
		for (int i=0; i<36; i++)
		{
			goal_id[i] = data.goal_id.uuid[i];
		}

    	{{data.GoalSetFromROS2}}
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_SendGoal_Request& data) const
	{
		for (int i=0; i<36; i++)
		{
			data.goal_id.uuid[i] = goal_id[i];
		}

    	{{data.GoalSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_SendGoal_Response
{
	GENERATED_BODY()

public:
	bool accepted;
	int stamp_sec;
	uint stamp_nanosec;

	void SetFromROS2({{data.Group}}__action__{{data.NameCap}}_SendGoal_Response data)
	{
    	accepted = data.accepted;
		stamp_sec = data.stamp.sec;
		stamp_nanosec = data.stamp.nanosec;
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_SendGoal_Response& data) const
	{
    	data.accepted = accepted;
		data.stamp.sec = stamp_sec;
		data.stamp.nanosec = stamp_nanosec;
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_GetResult_Request
{
	GENERATED_BODY()

public:
  	TArray<uint, TFixedAllocator<16>> goal_id;

	void SetFromROS2({{data.Group}}__action__{{data.NameCap}}_GetResult_Request data)
	{
		for (int i=0; i<36; i++)
		{
			goal_id[i] = data.goal_id.uuid[i];
		}

	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_GetResult_Request& data) const
	{
		for (int i=0; i<36; i++)
		{
			data.goal_id.uuid[i] = goal_id[i];
		}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_GetResult_Response
{
	GENERATED_BODY()

public:
	int8 status;
	{{data.ResultTypes}}

	void SetFromROS2({{data.Group}}__action__{{data.NameCap}}_GetResult_Response data)
	{
		status = data.status;
    	{{data.ResultSetFromROS2}}
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_GetResult_Response& data) const
	{
		data.status = status;
    	{{data.ResultSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_FeedbackMessage
{
	GENERATED_BODY()

public:
  	TArray<uint, TFixedAllocator<16>> goal_id;
	{{data.FeedbackTypes}}

	void SetFromROS2({{data.Group}}__action__{{data.NameCap}}_FeedbackMessage data)
	{
		for (int i=0; i<36; i++)
		{
			goal_id[i] = data.goal_id.uuid[i];
		}

    	{{data.FeedbackSetFromROS2}}
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_FeedbackMessage& data) const
	{
		for (int i=0; i<36; i++)
		{
			data.goal_id.uuid[i] = goal_id[i];
		}
		
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
	void SetGoalRequest(const F{{data.StructName}}_SendGoal_Request Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalRequest(F{{data.StructName}}_SendGoal_Request& Goal) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetGoalResponse(const F{{data.StructName}}_SendGoal_Response Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalResponse(F{{data.StructName}}_SendGoal_Response& Goal) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetResultRequest(const F{{data.StructName}}_GetResult_Request Result);

  	UFUNCTION(BlueprintCallable)
	void GetResultRequest(F{{data.StructName}}_GetResult_Request& Result) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetResultResponse(const F{{data.StructName}}_GetResult_Response Result);

  	UFUNCTION(BlueprintCallable)
	void GetResultResponse(F{{data.StructName}}_GetResult_Response& Result) const;



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
