from scripts.fill_dataset.get_prs import fetch_all_prs

if __name__ == '__main__':
    # from scripts.fill_dataset.get_issues import fetch_all_issues
    # fetch_all_issues()
    fetch_all_prs()

    print("Dataset filled successfully.")