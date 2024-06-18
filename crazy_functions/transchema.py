from toolbox import update_ui
from toolbox import CatchException, report_exception
from toolbox import write_history_to_file, promote_file_to_downloadzone
from .crazy_utils import request_gpt_model_in_new_thread_with_ui_alive
fast_debug = False


def transchema_helper(file_manifest_source, file_manifest_target, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt):
    import time, os
    for index, fp in enumerate(file_manifest):
        if fp.split(".")[-1] == "docx":
            from docx import Document
            doc = Document(fp)
            file_content = "\n".join([para.text for para in doc.paragraphs])
        else:
           raise RuntimeError('请先将.doc文档转换为.docx文档。')

        # private_upload里面的文件名在解压zip后容易出现乱码（rar和7z格式正常），故可以只分析文章内容，不输入文件名
        from crazy_functions.pdf_fns.breakdown_txt import breakdown_text_to_satisfy_token_limit
        from request_llms.bridge_all import model_info
        max_token = model_info[llm_kwargs['llm_model']]['max_token']
        TOKEN_LIMIT_PER_FRAGMENT = max_token * 3 // 4
        paper_fragments = breakdown_text_to_satisfy_token_limit(txt=file_content, limit=TOKEN_LIMIT_PER_FRAGMENT, llm_model=llm_kwargs['llm_model'])
        this_paper_history = []
        for i, paper_frag in enumerate(paper_fragments):
            i_say = f'Please summarize the following，the file name is {os.path.relpath(fp, project_folder)}，the file content is ```{paper_frag}```'
            i_say_show_user = f'请对下面的文章片段做概述: {os.path.abspath(fp)}的第{i+1}/{len(paper_fragments)}个片段。'
            gpt_say = yield from request_gpt_model_in_new_thread_with_ui_alive(
                inputs=i_say,
                inputs_show_user=i_say_show_user,
                llm_kwargs=llm_kwargs,
                chatbot=chatbot,
                history=[],
                sys_prompt="Summarize the csv file."
            )

            chatbot[-1] = (i_say_show_user, gpt_say)
            history.extend([i_say_show_user,gpt_say])
            this_paper_history.extend([i_say_show_user,gpt_say])


        res = write_history_to_file(history)
        promote_file_to_downloadzone(res, chatbot=chatbot)
        chatbot.append(("完成了吗？", res))
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    res = write_history_to_file(history)
    promote_file_to_downloadzone(res, chatbot=chatbot)
    chatbot.append(("所有文件都总结完成了吗？", res))
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面


@CatchException
def transchema(txt, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt, user_request):
    import glob, os

    # 基本信息：功能、贡献者
    chatbot.append([
        "函数插件功能？",
        "批量总结Word文档。函数插件贡献者: JasonGuo1。注意, 如果是.doc文件, 请先转化为.docx格式。"])
    yield from update_ui(chatbot=chatbot, history=history) # 刷新界面

    # 尝试导入依赖，如果缺少依赖，则给出安装建议
    try:
        from docx import Document
    except:
        report_exception(chatbot, history,
                         a=f"解析项目: {txt}",
                         b=f"导入软件依赖失败。使用该模块需要额外依赖，安装方法```pip install --upgrade python-docx pywin32```。")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 清空历史，以免输入溢出
    history = []

    # 检测输入参数，如没有给定输入参数，直接退出
    if os.path.exists(txt):
        project_folder = txt
    else:
        if txt == "": txt = '空空如也的输入栏'
        report_exception(chatbot, history, a=f"解析项目: {txt}", b=f"找不到本地项目或无权访问: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 搜索需要处理的文件清单
    if txt.endswith('.docx') or txt.endswith('.doc'):
        file_manifest = [txt]
    else:
        file_manifest = [f for f in glob.glob(f'{project_folder}/**/*.docx', recursive=True)] + \
                        [f for f in glob.glob(f'{project_folder}/**/*.doc', recursive=True)]

    # 如果没找到任何文件
    if len(file_manifest) == 0:
        report_exception(chatbot, history, a=f"解析项目: {txt}", b=f"找不到任何.docx或doc文件: {txt}")
        yield from update_ui(chatbot=chatbot, history=history) # 刷新界面
        return

    # 开始正式执行任务
    yield from 解析docx(file_manifest, project_folder, llm_kwargs, plugin_kwargs, chatbot, history, system_prompt)