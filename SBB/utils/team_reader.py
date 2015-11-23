from ..core.program import Program
from ..core.team import Team
from ..core.instruction import Instruction

def read_team_from_json(team_descriptor):
    programs = []
    for program_descriptor in team_descriptor['programs']:
        instructions = []
        for instruction_descriptor in program_descriptor['instructions']:
            instruction = Instruction(mode = instruction_descriptor['mode'], 
                target = instruction_descriptor['target'], op = instruction_descriptor['op'], 
                source = instruction_descriptor['source'])
            instructions.append(instruction)
        program = Program(-1, instructions, program_descriptor['action'], 
            program_id = program_descriptor['program_id'])
        programs.append(program)
    return Team(-1, programs, team_id = team_descriptor['team_id'])