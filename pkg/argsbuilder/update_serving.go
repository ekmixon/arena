// Copyright 2018 The Kubeflow Authors
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//       http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License
package argsbuilder

import (
	"fmt"
	"github.com/kubeflow/arena/pkg/apis/types"
	log "github.com/sirupsen/logrus"
	"github.com/spf13/cobra"
	"reflect"
	"strings"
)

type UpdateServingArgsBuilder struct {
	args        *types.CommonUpdateServingArgs
	argValues   map[string]interface{}
	subBuilders map[string]ArgsBuilder
}

func NewUpdateServingArgsBuilder(args *types.CommonUpdateServingArgs) ArgsBuilder {
	s := &UpdateServingArgsBuilder{
		args:        args,
		argValues:   map[string]interface{}{},
		subBuilders: map[string]ArgsBuilder{},
	}
	return s
}

func (s *UpdateServingArgsBuilder) GetName() string {
	items := strings.Split(fmt.Sprintf("%v", reflect.TypeOf(*s)), ".")
	return items[len(items)-1]
}

func (s *UpdateServingArgsBuilder) AddSubBuilder(builders ...ArgsBuilder) ArgsBuilder {
	for _, b := range builders {
		s.subBuilders[b.GetName()] = b
	}
	return s
}

func (s *UpdateServingArgsBuilder) AddArgValue(key string, value interface{}) ArgsBuilder {
	for name := range s.subBuilders {
		s.subBuilders[name].AddArgValue(key, value)
	}
	s.argValues[key] = value
	return s
}

func (s *UpdateServingArgsBuilder) AddCommandFlags(command *cobra.Command) {
	for name := range s.subBuilders {
		s.subBuilders[name].AddCommandFlags(command)
	}
	var (
		envs []string
	)

	command.Flags().StringVar(&s.args.Name, "name", "", "the serving name")
	command.Flags().StringVar(&s.args.Version, "version", "", "the serving version")
	command.Flags().StringVar(&s.args.Image, "image", "", "the docker image name of serving job")
	command.Flags().IntVar(&s.args.GPUCount, "gpus", 0, "the limit GPU count of each replica to run the serve.")
	command.Flags().IntVar(&s.args.GPUMemory, "gpumemory", 0, "the limit GPU memory of each replica to run the serve.")
	command.Flags().StringVar(&s.args.Cpu, "cpu", "", "the request cpu of each replica to run the serve.")
	command.Flags().StringVar(&s.args.Memory, "memory", "", "the request memory of each replica to run the serve.")
	command.Flags().IntVar(&s.args.Replicas, "replicas", 0, "the replicas number of the serve job.")
	command.Flags().StringArrayVarP(&envs, "env", "e", []string{}, "the environment variables")
	command.Flags().StringVar(&s.args.Command, "command", "", "the command will inject to container's command.")

	s.AddArgValue("env", &envs)
}

func (s *UpdateServingArgsBuilder) PreBuild() error {
	for name := range s.subBuilders {
		if err := s.subBuilders[name].PreBuild(); err != nil {
			return err
		}
	}
	if err := s.checkNamespace(); err != nil {
		return err
	}

	if err := s.checkName(); err != nil {
		return err
	}

	//if err := s.checkVersion(); err != nil {
	//	return err
	//}

	if err := s.checkReplicas(); err != nil {
		return err
	}

	if err := s.setEnvs(); err != nil {
		return err
	}

	return nil
}

func (s *UpdateServingArgsBuilder) Build() error {
	for name := range s.subBuilders {
		if err := s.subBuilders[name].Build(); err != nil {
			return err
		}
	}

	return nil
}

func (s *UpdateServingArgsBuilder) setEnvs() error {
	argKey := "env"
	var envs *[]string
	value, ok := s.argValues[argKey]
	if !ok {
		return nil
	}
	envs = value.(*[]string)
	s.args.Envs = transformSliceToMap(*envs, "=")
	return nil
}

func (s *UpdateServingArgsBuilder) checkNamespace() error {
	if s.args.Namespace == "" {
		return fmt.Errorf("namespace not set, please set it")
	}
	log.Debugf("namespace is %v", s.args.Namespace)
	return nil
}

func (s *UpdateServingArgsBuilder) checkName() error {
	if s.args.Name == "" {
		return fmt.Errorf("name not set, please set it")
	}
	log.Debugf("name is %v", s.args.Name)
	return nil
}

func (s *UpdateServingArgsBuilder) checkVersion() error {
	if s.args.Version == "" {
		return fmt.Errorf("version not set, please set it")
	}
	log.Debugf("version is %v", s.args.Version)
	return nil
}

func (s *UpdateServingArgsBuilder) checkReplicas() error {
	if s.args.Replicas < 0 {
		return fmt.Errorf("replicas not valid, must be greater than 0")
	}
	log.Debugf("replicas is %d", s.args.Replicas)
	return nil
}
