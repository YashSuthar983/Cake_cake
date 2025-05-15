import pandas as pd
import time

def generate_data(filepath="data/simulated_cloud_data.csv"):
    """Generates a simple simulated cloud data CSV."""
    data = []
    base_time = int(time.time()) - 1000 # Start time a bit in the past

    # Normal activities
    data.append(['user_1', 'user', 'vm_a', 'resource', 'accesses', base_time + 10, 10, 0.5])
    data.append(['user_1', 'user', 's3_b', 'resource', 'accesses', base_time + 70, 5, 0.2])
    data.append(['user_2', 'user', 'db_c', 'resource', 'accesses', base_time + 110, 15, 0.8])
    data.append(['vm_a', 'resource', 'sg_x', 'config', 'is_member_of', base_time + 160, 1, 0])
    data.append(['s3_b', 'resource', 'policy_p1', 'config', 'has_policy', base_time + 210, 1, 0])
    data.append(['user_2', 'user', 'vm_d', 'resource', 'accesses', base_time + 250, 12, 0.6])
    data.append(['vm_a', 'resource', 'vm_d', 'resource', 'network_conn', base_time + 300, 100, 0.1])
    data.append(['user_1', 'user', 'vm_d', 'resource', 'accesses', base_time + 350, 8, 0.4])

    # Simulate some potentially anomalous activities
    # User 3 is new/unusual and accesses sensitive data with high volume (feature1)
    data.append(['user_3_anomalous', 'user', 'db_c', 'resource', 'accesses', base_time + 400, 50, 0.9])
    # User 3 modifies a security group - high privilege action for potentially unusual user
    data.append(['user_3_anomalous', 'user', 'sg_y', 'config', 'modifies', base_time + 450, 1, 1.0])
    # Unusual connection between resources
    data.append(['vm_z_anomalous', 'resource', 'db_c', 'resource', 'network_conn', base_time + 500, 500, 0.95])


    df = pd.DataFrame(data, columns=['source_id', 'source_type', 'target_id', 'target_type', 'relationship_type', 'timestamp', 'feature1', 'feature2'])
    df.to_csv(filepath, index=False)
    print(f"Simulated data generated at {filepath}")

if __name__ == '__main__':
    generate_data()