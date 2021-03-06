// Copyright 2021 Rapyuta Robotics Co., Ltd.
// This code has been autogenerated from {{data.Filename}} - do not modify

#pragma once

#include <CoreMinimal.h>

#include "unique_identifier_msgs/msg/uuid.h"
#include "{{data.Group}}/action/{{data.Name}}.h"
#include "action_msgs/srv/cancel_goal.h"

#include "Actions/ROS2GenericAction.h"
#include "rclcUtilities.h"

#include "ROS2{{data.NameCap}}Action.generated.h"

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}SendGoalRequest
{
	GENERATED_BODY()

public:
  	TArray<uint, TFixedAllocator<16>> goal_id;
	{{data.GoalTypes}}

	void SetFromROS2(const {{data.Group}}__action__{{data.NameCap}}_SendGoal_Request& in_ros_data)
	{
		for (int i=0; i<16; i++)
		{
			goal_id[i] = in_ros_data.goal_id.uuid[i];
		}

    	{{data.GoalSetFromROS2}}
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_SendGoal_Request& out_ros_data) const
	{
		for (int i=0; i<16; i++)
		{
			out_ros_data.goal_id.uuid[i] = goal_id[i];
		}

    	{{data.GoalSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}SendGoalResponse
{
	GENERATED_BODY()

public:
	bool accepted;
	int stamp_sec;
	uint stamp_nanosec;

	void SetFromROS2(const {{data.Group}}__action__{{data.NameCap}}_SendGoal_Response& in_ros_data)
	{
    	accepted = in_ros_data.accepted;
		stamp_sec = in_ros_data.stamp.sec;
		stamp_nanosec = in_ros_data.stamp.nanosec;
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_SendGoal_Response& out_ros_data) const
	{
    	out_ros_data.accepted = accepted;
		out_ros_data.stamp.sec = stamp_sec;
		out_ros_data.stamp.nanosec = stamp_nanosec;
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}GetResultRequest
{
	GENERATED_BODY()

public:
  	TArray<uint, TFixedAllocator<16>> goal_id;

	void SetFromROS2(const {{data.Group}}__action__{{data.NameCap}}_GetResult_Request& in_ros_data)
	{
		for (int i=0; i<16; i++)
		{
			goal_id[i] = in_ros_data.goal_id.uuid[i];
		}

	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_GetResult_Request& out_ros_data) const
	{
		for (int i=0; i<16; i++)
		{
			out_ros_data.goal_id.uuid[i] = goal_id[i];
		}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}GetResultResponse
{
	GENERATED_BODY()

public:
	int8 status;
	{{data.ResultTypes}}

	void SetFromROS2(const {{data.Group}}__action__{{data.NameCap}}_GetResult_Response& in_ros_data)
	{
		status = in_ros_data.status;
    	{{data.ResultSetFromROS2}}
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_GetResult_Response& out_ros_data) const
	{
		out_ros_data.status = status;
    	{{data.ResultSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}FeedbackMessage
{
	GENERATED_BODY()

public:
  	TArray<uint, TFixedAllocator<16>> goal_id;
	{{data.FeedbackTypes}}

	void SetFromROS2(const {{data.Group}}__action__{{data.NameCap}}_FeedbackMessage& in_ros_data)
	{
		for (int i=0; i<16; i++)
		{
			goal_id[i] = in_ros_data.goal_id.uuid[i];
		}

    	{{data.FeedbackSetFromROS2}}
	}

	void SetROS2({{data.Group}}__action__{{data.NameCap}}_FeedbackMessage& out_ros_data) const
	{
		for (int i=0; i<16; i++)
		{
			out_ros_data.goal_id.uuid[i] = goal_id[i];
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
	void SetGoalRequest(const F{{data.StructName}}SendGoalRequest& Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalRequest(F{{data.StructName}}SendGoalRequest& Goal) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetGoalResponse(const F{{data.StructName}}SendGoalResponse& Goal);

  	UFUNCTION(BlueprintCallable)
	void GetGoalResponse(F{{data.StructName}}SendGoalResponse& Goal) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetResultRequest(const F{{data.StructName}}GetResultRequest& Result);

  	UFUNCTION(BlueprintCallable)
	void GetResultRequest(F{{data.StructName}}GetResultRequest& Result) const;
	
  	UFUNCTION(BlueprintCallable)
	void SetResultResponse(const F{{data.StructName}}GetResultResponse& Result);

  	UFUNCTION(BlueprintCallable)
	void GetResultResponse(F{{data.StructName}}GetResultResponse& Result) const;



  	UFUNCTION(BlueprintCallable)
	void SetFeedback(const F{{data.StructName}}FeedbackMessage& Feedback);

  	UFUNCTION(BlueprintCallable)
	void GetFeedback(F{{data.StructName}}FeedbackMessage& Feedback) const;
	
	virtual void* GetGoalRequest() override;
	virtual void* GetGoalResponse() override;
	virtual void* GetResultRequest() override;
	virtual void* GetResultResponse() override;
	virtual void* GetFeedbackMessage() override;

private:
	{{data.Group}}__action__{{data.NameCap}}SendGoalRequest {{data.NameCap}}_goal_request;
	{{data.Group}}__action__{{data.NameCap}}SendGoalResponse {{data.NameCap}}_goal_response;
	{{data.Group}}__action__{{data.NameCap}}GetResultRequest {{data.NameCap}}_result_request;
	{{data.Group}}__action__{{data.NameCap}}GetResultResponse {{data.NameCap}}_result_response;
	{{data.Group}}__action__{{data.NameCap}}FeedbackMessage {{data.NameCap}}_feedback_message;
};
