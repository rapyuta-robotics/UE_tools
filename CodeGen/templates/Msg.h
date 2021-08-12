// Copyright 2021 Rapyuta Robotics Co., Ltd.

#pragma once

#include "CoreMinimal.h"

#include "{{data.Group}}/msg/{{data.Name}}.h"

#include "Msgs/ROS2GenericMsg.h"
#include "rclcUtilities.h"

#include "ROS2{{data.NameCap}}Msg.generated.h"

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
class RCLUE_API UROS2{{data.NameCap}}Msg : public UROS2GenericMsg
{
	GENERATED_BODY()

public:
	virtual void Init() override;
	virtual void Fini() override;

	virtual const rosidl_message_type_support_t* GetTypeSupport() const override;
	
  	UFUNCTION(BlueprintCallable)
	void Update(const F{{data.StructName}} Input);
	
	virtual void* Get() override;

private:
	virtual const FString MsgToString() const override;

	{{data.Group}}__msg__{{data.NameCap}} {{data.Name}}_msg;
};
