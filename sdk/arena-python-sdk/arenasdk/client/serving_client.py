#!/usr/bin/env python
from __future__ import annotations
import json
from typing import List
from typing import Dict
from arenasdk.enums.types import *
from arenasdk.serving.job import ServingJob
from arenasdk.serving.serving_job_info import ServingJobInfo
from arenasdk.serving.serving_job_info import generate_serving_job_info
from arenasdk.common.util import Command
from arenasdk.exceptions.arena_exception import ArenaException

class ServingClient(object):
    def __init__(self,kubeconfig: str,namespace: str,loglevel: str,arena_namespace: str):
        self.kubeconfig = kubeconfig
        self.namespace = namespace
        self.loglevel = loglevel
        self.arena_namespace = arena_namespace

    def namespace(self,namespace: str) -> TrainingClient:
        return ServingClient(self.kubeconfig,namespace,self.loglevel,self.arena_namespace)

    def submit(self,job: TrainingJob) -> str:
        cmds = self.__generate_commands("serve")
        cmds.append(job.get_type().value[0])
        for opt in job.get_args():
            cmds.append(opt)
        cmds.append(job.get_command())
        try:
            status,stdout,stderr = Command(*cmds).run()
            if status != 0:
                err_message = f"the job {job.get_name()} is already exist, please delete it first."

                if stdout.find(err_message) != -1 or stderr.find(err_message) != -1:
                    raise ArenaException(ArenaErrorType.TrainingJobExistError,stdout + stderr)
                else:
                    raise ArenaException(ArenaErrorType.SubmitTrainingJobError,stdout + stderr)
            return stdout
        except ArenaException as e:
            raise e
    
    def list(self,job_type: ServingJobType,all_namespaces: bool) -> List[TrainingJobInfo]:
        def convert(json_object):
            job_infos = []
            for obj in json_object:
                job_infos.append(generate_serving_job_info(obj))
            return job_infos

        cmds = self.__generate_commands("list")
        if job_type not in [
            ServingJobType.AllServingJob,
            ServingJobType.UnknownServingJob,
        ]:
            cmds.append(f"--type={job_type.value}")
        if all_namespaces:
            cmds.append("-A")
        cmds.append("-o")
        cmds.append("json")
        try:
            status,stdout,stderr = Command(*cmds).run()
            if status != 0:
                raise ArenaException(ArenaErrorType.ListServingJobError,stdout + stderr)
            return json.loads(stdout,object_hook=convert)
        except ArenaException as e:
            raise e

    def get(self,job_name: str,job_type: ServingJobType,version: str) -> TrainingJobInfo:
        cmds = self.__generate_commands("serve","get")
        cmds.append(job_name)
        if job_type not in [
            ServingJobType.AllServingJob,
            ServingJobType.UnknownServingJob,
        ]:
            cmds.append(f"--type={job_type.value[0]}")
        if version != "":
            cmds.append(f"--version={version}")
        cmds.append("-o")
        cmds.append("json")
        try:
            status,stdout,stderr = Command(*cmds).run()
            if status != 0:
                err_message = f"Not found serving job {job_name}"
                if stdout.find(err_message) != -1 or stderr.find(err_message) != -1:
                    return None
                else:
                    raise ArenaException(ArenaErrorType.GetServingJobError,stdout + stderr)
            data = json.loads(stdout)
            return generate_serving_job_info(data)
        except ArenaException as e:
            raise e
    
    def delete(self, job_name: str,job_type: ServingJobType,version: str) -> str:
        cmds = self.__generate_commands("serve","delete")
        cmds.append(job_name)
        if job_type not in [
            TrainingJobType.AllTrainingJob,
            TrainingJobType.UnknownTrainingJob,
        ]:
            cmds.append(f"--type={job_type.value[0]}")
        if version != "":
            cmds.append(f"--version={version}")
        try:
            status,stdout,stderr = Command(*cmds).run()
            if status != 0:
                raise ArenaException(ArenaErrorType.DeleteServingJobError,stdout + stderr)
            return stdout
        except ArenaException as e:
            raise e

    def traffic_router_split(self,job_name: str,job_type: ServingJobType,version_weights: Dict[str,int]):
        cmds = self.__generate_commands("serve","traffic-router-split")
        cmds.append(f"--name={job_name}")
        for version,weight in version_weights.items():
            cmds.append(f"-v={version}:{str(weight)}")
        try:
            status,stdout,stderr = Command(*cmds).run()
            if status != 0:
                raise ArenaException(ArenaErrorType.TrafficRouterSplitServingJobError,stdout + stderr)
            return stdout
        except ArenaException as e:
            raise e
        
         
    def __generate_commands(self,*sub_commands: List[str]) -> List[str]:
        arena_cmds = [ARENA_BINARY]
        arena_cmds.extend(iter(sub_commands))
        if self.kubeconfig != "":
            arena_cmds.append(f"--config={self.kubeconfig}")
        if self.namespace != "":
            arena_cmds.append(f"--namespace={self.namespace}")
        if self.arena_namespace != "":
            arena_cmds.append(f"--arena-namespace={self.arena_namespace}")
        if self.loglevel != "":
            arena_cmds.append(f"--loglevel={self.loglevel}")
        return arena_cmds
        		
