// Copyright 2021 Rapyuta Robotics Co., Ltd.

#pragma once

#include "CoreMinimal.h"

#include "Srvs/ROS2GenericSrv.h"
#include "rclcUtilities.h"
#include "{{data.Group}}/srv/{{data.Name}}.h"

#include "ROS2{{data.NameCap}}Srv.generated.h"

/**
 * 
 */
UCLASS()
class RCLUE_API UROS2{{data.NameCap}}Srv : public UROS2GenericSrv
{
	GENERATED_BODY()

public:
  	UFUNCTION(BlueprintCallable)
	virtual void Init() override;

  	UFUNCTION(BlueprintCallable)
	virtual void Fini() override;

	virtual const rosidl_service_type_support_t* GetTypeSupport() const override;
	
	// used by client
  	UFUNCTION(BlueprintCallable)
	void SetInputs(/* TODO: Fill here */);
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void GetInputs(/* TODO: Fill here */) const;
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void SetOutput(/* TODO: Fill here */);
	
	// used by client
  	UFUNCTION(BlueprintCallable)
	void GetOutput(/* TODO: Fill here */) const;
	
	virtual void* GetRequest() override;
	virtual void* GetResponse() override;

private:
	virtual const FString SrvRequestToString() const override;
	virtual const FString SrvResponseToString() const override;

	{{data.Group}}__srv__{{data.NameCap}}_Request {{data.NameCap}}_req;
	{{data.Group}}__srv__{{data.NameCap}}_Response {{data.NameCap}}_res;
};
