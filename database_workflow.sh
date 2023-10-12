#!/bin/bash

echo "PlanetScale Branching Guide with pscale"
echo "--------------------------------------"
echo ""

read -p "Enter the name of the database (e.g., elmo-db): " database
read -p "Enter the name of the branch you want to operate on: " branch_name

# Step 1: Create a new branch
read -p "Do you want to create a new branch? (yes/no): " create_branch
if [ "$create_branch" == "yes" ]; then
    pscale branch create $database $branch_name
fi

# Step 2: Connect to your branch
read -p "Do you want to connect to the branch? (yes/no): " connect_branch
if [ "$connect_branch" == "yes" ]; then
    echo "Please connect to the branch using the following command in a separate terminal window:"
    echo "pscale connect $database $branch_name"
    echo ""
    read -p "Once you've successfully connected in the other terminal, type 'yes' to continue: " connected
    while [ "$connected" != "yes" ]; do
        read -p "If you have not connected yet, please do so. Once done, type 'yes' to continue: " connected
    done
fi

# Step 3: Generate and apply database migrations
read -p "Generate migration scripts using Alembic? (yes/no): " alembic_generate
if [ "$alembic_generate" == "yes" ]; then
    read -p "Enter a description for the changes: " description
    alembic current
    alembic stamp head
    alembic revision --autogenerate -m "$description"
    alembic upgrade head
fi

# Step 4: Review changes
echo "To Review the differences between the branch and main? run `pscale branch diff $database $branch_name`"

read -p "Request deployment? (yes/no): " merge_changes
if [ "$merge_changes" == "yes" ]; then
    pscale deploy-request create $database $branch_name
fi

echo "Script completed!"
