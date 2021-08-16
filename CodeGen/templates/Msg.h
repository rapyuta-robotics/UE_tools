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
    	{{data.SetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}& data) const
	{
    	{{data.SetROS2}}
	}
};

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
	
	// TODO these are for a future refactoring, as it requires to adapt the rest of the codes
  	UFUNCTION(BlueprintCallable)
	void SetMsg(const F{{data.StructName}} Input);
	
  	UFUNCTION(BlueprintCallable)
	void GetMsg(F{{data.StructName}}& Output);
	
	virtual void* Get() override;

private:
	virtual FString MsgToString() const override;

	{{data.Group}}__msg__{{data.NameCap}} {{data.Name}}_msg;
};
