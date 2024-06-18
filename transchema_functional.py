import pandas as pd  # Ensure pandas is imported

def transform(source_file_upload, target_file_upload):
    """
    Summarizes the task by processing the source and target CSV files and returning the result.

    Args:
        source_file_upload (list): A list of uploaded source CSV files.
        target_file_upload (list): A list of uploaded target CSV files.

    Returns:
        list: A list containing the result of the task. Each element of the list is a sublist with two elements:
              - The user's input representation.
              - The result of the task.
    """
    message = ""
    html_tables = ""
    
    # CSS style for scrollable table
    scrollable_table_style = '<div style="overflow-x: auto;">'
    
    # [step 1]>> Summarize the transformation task
     
    # Process the source CSV files
    for file in source_file_upload:
        df = pd.read_csv(file.name)
        # Wrap the DataFrame HTML in a div with style for scrolling
        html_tables += f"{scrollable_table_style}{df.to_html()}</div><br>"
        message += f"Processed source file: {file.name}<br>"
    
    # Process the target CSV file
    target_df = pd.read_csv(target_file_upload[0].name)
    # Wrap the DataFrame HTML in a div with style for scrolling
    html_tables += f"{scrollable_table_style}{target_df.to_html()}</div><br>"
    message += f"Processed target file: {target_file_upload[0].name}<br>"
    
    # Combine the message with the HTML tables
    full_message = message + html_tables
    inputs_show_user = "User's input representation"
    gpt_res = full_message
    res = []
    res.append([inputs_show_user, gpt_res])

    # [step 1]>> Summarize the transformation task
    # Define/show the task to perform

    # [step 2]>> Show which profilings are done
    # Confirm that the profilling is done
    # State which profilling results are used for summary

    ################ Iterative Improvements #################
    # [step 3]>> Show results for iteration 1 ~ max_iter
    # Highlight improvement for each iteration would be great
    # Highlight quality feedback and other feedback

    # [step 4]>> Confirm that the transformation is done
    # output the cost/latency





    return res

