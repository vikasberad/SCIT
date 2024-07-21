# ai_planner_2.py

import sys

def main(domain_file, problem_file, output_file):
    # Simple placeholder for an AI planner
    # In a real scenario, you'd call an actual AI planner here
    with open(output_file, 'w') as f:
        if 'HighProb' in problem_file:
            if 'temp' in domain_file:
                f.write('turn_on_fan\n')
            elif 'light' in domain_file:
                f.write('turn_on_light\n')
            elif 'hum' in domain_file:
                f.write('turn_off_humidity\n')
        elif 'LowProb' in problem_file:
            if 'temp' in domain_file:
                f.write('turn_on_heater\n')
            elif 'light' in domain_file:
                f.write('turn_off_light\n')
            elif 'hum' in domain_file:
                f.write('turn_on_humidity\n')
        else:
            f.write('turn_off_heater\nturn_off_fan\n')

if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python ai_planner_2.py <domain_file> <problem_file> <output_file>")
        sys.exit(1)
    
    domain_file = sys.argv[1]
    problem_file = sys.argv[2]
    output_file = sys.argv[3]
    
    main(domain_file, problem_file, output_file)
