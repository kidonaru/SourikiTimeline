import os
import gradio as gr
from gradio_modal import Modal

from scripts.chara_skill import CharaSkill
from scripts.common_utils import load_timeline
from scripts.config_utils import AppConfig, ProjectConfig, get_timeline_columns
from scripts.gradio_utils import download_video_gr, mask_preview_gr, save_mask_gr, timeline_generate_gr, create_project_gr, reload_workspace_gr, select_project_gr, select_workspace_gr, timeline_update_gr, load_mask_gr

movie_downloaders = ["pytube", "yt-dlp"]
download_formats = ["mp4", "webm"]
chara_names = [x.chara_name for x in CharaSkill.from_tsv()]
chara_names.sort()
tsv_separators = [("タブ", "\t"), ("スペース", " "), ("カンマ", ",")]

app_config = AppConfig.instance()
config = ProjectConfig.load(app_config.project_path)

source_dataframe = load_timeline(app_config.project_path)
dataframe, dataframe_tsv = config.convert_timeline_and_tsv(source_dataframe)

def get_mask_image_names():
    return [f for f in os.listdir(os.path.join("resources", "mask")) if f.endswith(".png")]

def add_space(space_count:int=1):
    for i in range(0, space_count):
        gr.HTML(value="")

js = """
function () {
    gradioURL = window.location.href
    if (!gradioURL.endsWith('?__theme=dark')) {
        window.location.replace(gradioURL + '?__theme=dark');
    }
}
"""

with gr.Blocks(title="総力戦タイムラインメーカー", js=js) as demo:
    gr.Markdown("総力戦タイムラインメーカー")

    with gr.Row():
        with gr.Column(scale=1, min_width=150):
            project_image = gr.Image(show_label=False, value=app_config.get_current_preimage(), width=150)
        with gr.Column(scale=3):
            with gr.Row():
                project_path_textbox = gr.Textbox(label="動画保存フォルダ", value=app_config.project_path, visible=False)
                title_textbox = gr.Textbox(label="タイトル", value=config.title, interactive=False)

        with gr.Column(scale=3):
            base_output = gr.Markdown(show_label=False)

    with gr.Tabs():
        with gr.TabItem("動画一覧"):
            with gr.Row():
                with gr.Column(scale=1.5):
                    add_space(1)
                    with gr.Row():
                        show_create_project_button = gr.Button("新規作成", variant="primary")
                        workspace_reload_button = gr.Button("リスト更新", variant="primary")
                    workspace_gallery = gr.Gallery(value=app_config.get_all_gallery(), columns=4, allow_preview=False)
                with gr.Column(scale=1):
                    with gr.Row():
                        with gr.Column(scale=5):
                            workspace_path_textbox = gr.Textbox(label="ワークスペースパス", value=app_config.workspace_path, info="動画/タイムラインの保存先ディレクトリ", interactive=False)
                        with gr.Column(scale=1, min_width=50):
                            workspace_open_button = gr.Button("選択", variant="primary")

                    auto_save_checkbox = gr.Checkbox(value=app_config.auto_save, label="Auto Save", visible=False)
                    thumbnail_width_slider = gr.Number(value=app_config.thumbnail_width, label="Thumbnail Width", visible=False)
                    thumbnail_height_slider = gr.Number(value=app_config.thumbnail_height, label="Thumbnail Height", visible=False)
                    thumbnail_file_textbox = gr.Textbox(label="Thumbnail File Name", value=config.movie_thumbnail_file_name, visible=False)

                    movie_url_textbox = gr.Textbox(label="Youtube URL", value=config.movie_url, interactive=False)
                    artist_textbox = gr.Textbox(label="投稿者", value=config.author, interactive=False)

        with gr.TabItem("ダウンロード"):
            with gr.Row():
                with gr.Column():
                    add_space(1)
                    with gr.Row():
                        movie_download_button = gr.Button("動画ダウンロード", variant="primary")
                    with gr.Row():
                        downloader_dropdown = gr.Dropdown(movie_downloaders, value=app_config.downloader, label="ダウンローダー")
                        download_format_dropdown = gr.Dropdown(download_formats, value=app_config.download_format, label="フォーマット")
                        movie_download_file_textbox = gr.Textbox(label="ダウンロードファイル名", value=config.movie_download_file_name, visible=False)
                with gr.Column():
                    add_space(1)

        with gr.TabItem("マスク調整"):
            with gr.Row():
                with gr.Column():
                    add_space(1)
                    with gr.Row():
                        mask_preview_button = gr.Button("プレビュー更新", variant="primary")
                    with gr.Tabs():
                        with gr.TabItem("プレビュー設定"):
                            with gr.Row():
                                movie_preview_time_slider = gr.Slider(value=config.movie_preview_time, label="プレビュー時間(秒)", info="スキル発動時間に合わせて手動調整してください", minimum=config.movie_start_time, maximum=config.movie_end_time, step=0.1)
                            with gr.Accordion("動画クロップ設定"):
                                with gr.Row():
                                    movie_x_slider = gr.Number(value=config.movie_x, label="X")
                                    movie_y_slider = gr.Number(value=config.movie_y, label="Y")
                                with gr.Row():
                                    movie_width_slider = gr.Number(value=config.movie_width, label="Width")
                                    movie_height_slider = gr.Number(value=config.movie_height, label="Height")
                            with gr.Accordion("タイムライン対象時間(秒)"):
                                with gr.Row():
                                    movie_start_time_slider = gr.Number(value=config.movie_start_time, label="Start")
                                    movie_end_time_slider = gr.Number(value=config.movie_end_time, label="End")
                        with gr.TabItem("マスク設定"):
                            add_space(1)
                            with gr.Row():
                                show_load_mask_button = gr.Button("マスクのロード", variant="primary")
                                show_save_mask_button = gr.Button("マスクの保存", variant="primary")
                            with gr.Accordion("スキルマスク範囲(赤枠)", open=False):
                                with gr.Row():
                                    mask_skill_x_slider = gr.Number(value=config.mask_skill_x, label="X")
                                    mask_skill_y_slider = gr.Number(value=config.mask_skill_y, label="Y")
                                with gr.Row():
                                    mask_skill_w_slider = gr.Number(value=config.mask_skill_w, label="Width")
                                    mask_skill_h_slider = gr.Number(value=config.mask_skill_h, label="Height")
                            with gr.Accordion("コストマスク範囲(青枠)", open=False):
                                with gr.Row():
                                    mask_cost_x_slider = gr.Number(value=config.mask_cost_x, label="X")
                                    mask_cost_y_slider = gr.Number(value=config.mask_cost_y, label="Y")
                                with gr.Row():
                                    mask_cost_w_slider = gr.Number(value=config.mask_cost_w, label="Width")
                                    mask_cost_h_slider = gr.Number(value=config.mask_cost_h, label="Height")
                            with gr.Accordion("時間マスク範囲(緑枠)", open=False):
                                with gr.Row():
                                    mask_time_x_slider = gr.Number(value=config.mask_time_x, label="X")
                                    mask_time_y_slider = gr.Number(value=config.mask_time_y, label="Y")
                                with gr.Row():
                                    mask_time_w_slider = gr.Number(value=config.mask_time_w, label="Width")
                                    mask_time_h_slider = gr.Number(value=config.mask_time_h, label="Height")
                            with gr.Accordion("コストバー設定", open=False):
                                with gr.Row():
                                    mask_cost_color1_textbox = gr.ColorPicker(value=config.mask_cost_color1, label="基準色", info="コストバー判定に使用する基準色 デフォルト(0, 180, 250)")
                                    mask_cost_color2_textbox = gr.ColorPicker(value=config.mask_cost_color2, label="エフェクト色", info="コストバー判定に使用するエフェクト色 デフォルト(255, 255, 255)")
                                    mask_cost_color_threshold_slider = gr.Number(value=config.mask_cost_color_threshold, label="色の誤差許容値", info="デフォルト20")
                            mask_image_w_slider = gr.Number(value=config.mask_image_w, label="Width", visible=False)
                            mask_image_h_slider = gr.Number(value=config.mask_image_h, label="Height", visible=False)

                with gr.Column():
                    movie_preview_image = gr.Image(label="Preview Image", interactive=False)
                    movie_input_video = gr.Video(label="Download Video")

        with gr.TabItem("タイムライン生成"):
            with gr.Row():
                with gr.Column():
                    with gr.Tabs():
                        with gr.TabItem("生成設定"):
                            add_space(1)
                            with gr.Row():
                                timeline_generate_button = gr.Button("タイムライン生成", variant="primary")
                            with gr.Row():
                                movie_frame_rate_slider = gr.Slider(value=config.movie_frame_rate, label="読み取りフレームレート", minimum=0, maximum=60, step=1)
                            with gr.Row():
                                timeline_ignore_chara_names_dropdown = gr.Dropdown(chara_names, value=config.timeline_ignore_chara_names, multiselect=True, label="除外キャラ名一覧", info="ギミックの文字などで誤認識する場合に指定")
                            with gr.Row():
                                timeline_max_time_number = gr.Number(value=config.timeline_max_time, label="バトルの制限時間(秒)")
                        with gr.TabItem("表示設定(共通)"):
                            add_space(1)
                            with gr.Row():
                                timeline_update_button = gr.Button("表示更新", variant="primary")
                            with gr.Row():
                                timeline_visible_columns_checkbox = gr.CheckboxGroup(label="表示カラム", choices=get_timeline_columns(), value=app_config.timeline_visible_columns)
                            with gr.Row():
                                timeline_cost_omit_seconds_slider = gr.Slider(value=app_config.timeline_cost_omit_seconds, label="コストを省略する秒数", info="前回のスキルを発動してからの経過時間が指定秒数以下の場合、コストの表示は省略されます", minimum=0, maximum=10, step=0.1)
                            with gr.Row():
                                timeline_newline_chara_names_dropdown = gr.Dropdown(chara_names, value=app_config.timeline_newline_chara_names, multiselect=True, label="改行するキャラ名一覧", info="指定したキャラがスキル発動後、改行する")
                            with gr.Row():
                                timeline_tsv_separator_dropdown = gr.Dropdown(choices=tsv_separators, value=app_config.timeline_tsv_separator, label="TSVの区切り文字")

                with gr.Column():
                    with gr.Tabs():
                        with gr.TabItem("Table"):
                            timeline_dataframe = gr.Dataframe(dataframe, interactive=False)
                        with gr.TabItem("TSV"):
                            timeline_dataframe_tsv = gr.Textbox(dataframe_tsv, show_label=False, interactive=False, lines=20)

    # プロジェクト作成モーダル
    with Modal(visible=False) as create_project_modal:
        with gr.Row():
            with gr.Column(scale=1.5):
                create_project_url_textbox = gr.Textbox(label="タイムライン出力する動画のURL", value="", info="タイムラインの出力をしたいYouTubeのURLを入力してください")
                create_project_button = gr.Button("作成", variant="primary")
            with gr.Column(scale=1):
                create_project_output = gr.Markdown(show_label=False)

    # マスクのロードモーダル
    with Modal(visible=False) as load_mask_modal:
        with gr.Row():
            with gr.Column(scale=1.5):
                mask_image_name_dropdown = gr.Dropdown(get_mask_image_names(), value=config.mask_image_name, label="マスク画像名", info="OCRで読み取るマスク範囲を選択します。resources\maskに格納されている画像を使用できます")
                load_mask_button = gr.Button("ロード", variant="primary")
            with gr.Column(scale=1):
                load_mask_output = gr.Markdown(show_label=False)
        add_space(10)

    # マスクの保存モーダル
    with Modal(visible=False) as save_mask_modal:
        with gr.Row():
            with gr.Column(scale=1.5):
                save_mask_image_name_text = gr.Textbox(label="マスク画像名", info="保存するファイル名を入力してください。resources\maskに保存されます")
                save_mask_button = gr.Button("保存", variant="primary")
            with gr.Column(scale=1):
                save_mask_output = gr.Markdown(show_label=False)

    # 画像確認モーダル
    with Modal(visible=False) as confirm_image_modal:
        confirm_image = gr.Image(show_label=False)

    app_config_inputs = [
        project_path_textbox,
        workspace_path_textbox,
        auto_save_checkbox,
        download_format_dropdown,
        downloader_dropdown,
        thumbnail_width_slider,
        thumbnail_height_slider,

        timeline_tsv_separator_dropdown,
        timeline_visible_columns_checkbox,
        timeline_cost_omit_seconds_slider,
        timeline_newline_chara_names_dropdown,
    ]

    inputs = [
        title_textbox,
        artist_textbox,

        movie_url_textbox,
        movie_download_file_textbox,
        thumbnail_file_textbox,
        movie_start_time_slider,
        movie_end_time_slider,
        movie_x_slider,
        movie_y_slider,
        movie_width_slider,
        movie_height_slider,
        movie_frame_rate_slider,
        movie_preview_time_slider,

        mask_image_name_dropdown,

        mask_image_w_slider,
        mask_image_h_slider,

        mask_skill_x_slider,
        mask_skill_y_slider,
        mask_skill_w_slider,
        mask_skill_h_slider,

        mask_cost_x_slider,
        mask_cost_y_slider,
        mask_cost_w_slider,
        mask_cost_h_slider,

        mask_time_x_slider,
        mask_time_y_slider,
        mask_time_w_slider,
        mask_time_h_slider,

        mask_cost_color1_textbox,
        mask_cost_color2_textbox,
        mask_cost_color_threshold_slider,

        timeline_ignore_chara_names_dropdown,
        timeline_max_time_number,
    ]

    outputs = [
        movie_preview_image,
        movie_input_video,
    ]

    mask_outputs = [
        mask_image_w_slider,
        mask_image_h_slider,

        mask_skill_x_slider,
        mask_skill_y_slider,
        mask_skill_w_slider,
        mask_skill_h_slider,

        mask_cost_x_slider,
        mask_cost_y_slider,
        mask_cost_w_slider,
        mask_cost_h_slider,

        mask_time_x_slider,
        mask_time_y_slider,
        mask_time_w_slider,
        mask_time_h_slider,
    ]

    show_create_project_button.click(lambda: Modal(visible=True),
                                     inputs=None,
                                     outputs=create_project_modal
                                )

    def show_load_mask_modal():
        modal = Modal(visible=True)
        dropdown = gr.update(choices=get_mask_image_names())

        return [modal, dropdown]

    show_load_mask_button.click(show_load_mask_modal,
                                inputs=None,
                                outputs=[
                                    load_mask_modal,
                                    mask_image_name_dropdown
                                ]
                            )

    show_save_mask_button.click(lambda: Modal(visible=True),
                                inputs=None,
                                outputs=save_mask_modal
                            )

    def show_confirm_image_modal(image):
        modal = Modal(visible=True)
        return [modal, image]

    movie_preview_image.select(show_confirm_image_modal,
                                inputs=movie_preview_image,
                                outputs=[
                                    confirm_image_modal,
                                    confirm_image
                                ]
                            )

    workspace_open_button.click(select_workspace_gr,
                                  inputs=[],
                                  outputs=[
                                        base_output,
                                        workspace_path_textbox,
                                  ])

    workspace_gallery.select(select_project_gr,
                             inputs=[],
                             outputs=[
                                    base_output,
                                    project_path_textbox,
                                    project_image,
                                    timeline_dataframe,
                                    timeline_dataframe_tsv,
                                    *inputs,
                                    *outputs,
                             ])

    create_project_button.click(create_project_gr,
                                  inputs=[
                                        create_project_url_textbox,
                                  ],
                                  outputs=[
                                        create_project_output,
                                        project_path_textbox,
                                        project_image,
                                        timeline_dataframe,
                                        timeline_dataframe_tsv,
                                        *inputs,
                                        *outputs,
                                  ])

    workspace_reload_button.click(reload_workspace_gr,
                                  inputs=[],
                                  outputs=workspace_gallery)

    movie_download_button.click(download_video_gr,
                          inputs=[
                                *app_config_inputs,
                                *inputs,
                          ],
                          outputs=[
                                base_output,
                                movie_input_video,
                                movie_preview_image,
                                movie_end_time_slider,
                                movie_width_slider,
                                movie_height_slider,
                                movie_preview_time_slider,
                                *mask_outputs,
                          ])

    mask_preview_button.click(mask_preview_gr,
                          inputs=[
                                *app_config_inputs,
                                *inputs,
                          ],
                          outputs=[
                                base_output,
                                movie_input_video,
                                movie_preview_image,
                                movie_preview_time_slider,
                          ])

    load_mask_button.click(load_mask_gr,
                            inputs=[
                                *app_config_inputs,
                                *inputs,
                            ],
                            outputs=[
                                load_mask_output,
                                movie_input_video,
                                movie_preview_image,
                                movie_preview_time_slider,
                                *mask_outputs,
                            ])

    save_mask_button.click(save_mask_gr,
                            inputs=[
                                save_mask_image_name_text,
                            ],
                            outputs=[
                                save_mask_output,
                                mask_image_name_dropdown,
                                *mask_outputs,
                            ])

    timeline_generate_button.click(timeline_generate_gr,
                          inputs=[
                                *app_config_inputs,
                                *inputs,
                          ],
                          outputs=[
                                base_output,
                                timeline_dataframe,
                                timeline_dataframe_tsv,
                          ])

    timeline_update_button.click(timeline_update_gr,
                          inputs=[
                                *app_config_inputs,
                                *inputs,
                          ],
                          outputs=[
                                base_output,
                                timeline_dataframe,
                                timeline_dataframe_tsv,
                          ])

if __name__ == "__main__":
    demo.launch(inbrowser=True)
