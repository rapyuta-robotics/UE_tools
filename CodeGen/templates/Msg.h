// Copyright 2021 Rapyuta Robotics Co., Ltd.

#pragma once

#include "CoreMinimal.h"

#include "{{data.Group}}/msg/{{data.Name}}.h"

#include "Msgs/ROS2GenericMsg.h"
#include "rclcUtilities.h"

#include "ROS2{{data.NameCap}}Msg.generated.h"

/**
 * 
 */
UCLASS()
class RCLUE_API UROS2{{data.NameCap}}Msg : public UROS2GenericMsg
{
	GENERATED_BODY()

public:
	virtual void Init() override;
	virtual void Fini() override;

	virtual const rosidl_message_type_support_t* GetTypeSupport() const override;
	
  	UFUNCTION(BlueprintCallable)
	void Update(/* TODO: Fill here */);
	
	virtual void* Get() override;

private:
	virtual const FString MsgToString() const override;

	{{data.Group}}__msg__{{data.NameCap}} {{data.Name}}_pub_msg;
};
