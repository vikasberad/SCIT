import pddlpy

def generate_plan(domain_file, problem_file):
    # Load the domain and problem files
    domain_problem = pddlpy.DomainProblem(domain_file, problem_file)

    # Initialize the planner
    planner = pddlpy.Planner()

    # Generate the plan
    plan = planner.plan(domain_problem)
    
    # Extracting the action names from the plan
    actions = [str(action) for action in plan]

    return actions

if __name__ == "__main__":
    import sys
    domain_file = sys.argv[1]
    problem_file = sys.argv[2]
    plan = generate_plan(domain_file, problem_file)
    for action in plan:
        print(action)
