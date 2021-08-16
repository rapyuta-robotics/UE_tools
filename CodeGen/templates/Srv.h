// Copyright 2021 Rapyuta Robotics Co., Ltd.

#pragma once

#include "CoreMinimal.h"

#include "Srvs/ROS2GenericSrv.h"
#include "rclcUtilities.h"
#include "{{data.Group}}/srv/{{data.Name}}.h"

#include "ROS2{{data.NameCap}}Srv.generated.h"

// potential problem: if this struct is defined multiple times!
USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_Request
{
	GENERATED_BODY()

public:
	{{data.ReqTypes}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}}_Request data)
	{
    	{{data.ReqSetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}_Request& data) const
	{
    	{{data.ReqSetROS2}}
	}
};

USTRUCT(Blueprintable)
struct RCLUE_API F{{data.StructName}}_Response
{
	GENERATED_BODY()

public:
	{{data.ResTypes}}

	void SetFromROS2({{data.Group}}__msg__{{data.NameCap}}_Response data)
	{
    	{{data.ResSetFromROS2}}
	}

	void SetROS2({{data.Group}}__msg__{{data.NameCap}}_Response& data) const
	{
    	{{data.ResSetROS2}}
	}
};

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
	void SetInputs(const F{{data.StructName}}_Request Input);
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void GetInputs(F{{data.StructName}}_Request& Input) const;
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void SetOutput(const F{{data.StructName}}_Response Output);
	
	// used by client
  	UFUNCTION(BlueprintCallable)
	void GetOutput(F{{data.StructName}}_Response& Output) const;
	
	// TODO these are for a future refactoring, as it requires to adapt the rest of the codes
	// used by client
  	UFUNCTION(BlueprintCallable)
	void SetRequest(const F{{data.StructName}}_Request Request);
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void GetRequest(F{{data.StructName}}_Request& Request) const;
	
	// used by service
  	UFUNCTION(BlueprintCallable)
	void SetResponse(const F{{data.StructName}}_Response Response);
	
	// used by client
  	UFUNCTION(BlueprintCallable)
	void GetResponse(F{{data.StructName}}_Response& Response) const;
	
	virtual void* GetRequest() override;
	virtual void* GetResponse() override;

private:
	virtual const FString SrvRequestToString() const override;
	virtual const FString SrvResponseToString() const override;

	{{data.Group}}__srv__{{data.NameCap}}_Request {{data.NameCap}}_req;
	{{data.Group}}__srv__{{data.NameCap}}_Response {{data.NameCap}}_res;
};