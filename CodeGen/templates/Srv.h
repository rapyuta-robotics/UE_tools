// Copyright 2021 Rapyuta Robotics Co., Ltd.
// This code has been autogenerated from {{data.Filename}} - do not modify

#pragma once

#include <CoreMinimal.h>

#include "Srvs/ROS2GenericSrv.h"
#include "rclcUtilities.h"
#include "{{data.Group}}/srv/{{data.Name}}.h"

#include "ROS2{{data.NameCap}}Srv.generated.h"

// potential problem: if this struct is defined multiple times!
USTRUCT(Blueprintable)
struct {{data.ModuleAPI}} F{{data.StructName}}Request
{
	GENERATED_BODY()

public:
	{{data.ReqTypes}}

	void SetFromROS2(const {{data.Group}}__srv__{{data.NameCap}}_Request& in_ros_data)
	{
    	{{data.ReqSetFromROS2}}
	}

	void SetROS2({{data.Group}}__srv__{{data.NameCap}}_Request& out_ros_data) const
	{
    	{{data.ReqSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct {{data.ModuleAPI}} F{{data.StructName}}Response
{
	GENERATED_BODY()

public:
	{{data.ResTypes}}

	void SetFromROS2(const {{data.Group}}__srv__{{data.NameCap}}_Response& in_ros_data)
	{
    	{{data.ResSetFromROS2}}
	}

	void SetROS2({{data.Group}}__srv__{{data.NameCap}}_Response& out_ros_data) const
	{
    	{{data.ResSetROS2}}
	}
};

UCLASS()
class {{data.ModuleAPI}} UROS2{{data.NameCap}}Srv : public UROS2GenericSrv
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
	void SetRequest(const F{{data.StructName}}Request& Request);
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void GetRequest(F{{data.StructName}}Request& Request) const;
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void SetResponse(const F{{data.StructName}}Response& Response);
	
	// used by client
  	UFUNCTION(BlueprintCallable)
	void GetResponse(F{{data.StructName}}Response& Response) const;
	
	virtual void* GetRequest() override;
	virtual void* GetResponse() override;

private:
	virtual FString SrvRequestToString() const override;
	virtual FString SrvResponseToString() const override;

	{{data.Group}}__srv__{{data.NameCap}}_Request {{data.NameCap}}_req;
	{{data.Group}}__srv__{{data.NameCap}}_Response {{data.NameCap}}_res;
};
