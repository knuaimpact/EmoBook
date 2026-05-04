from huggingface_hub import snapshot_download

snapshot_download(
    repo_id="myshell-ai/OpenVoiceV2",
    local_dir="checkpoints_v2",
    local_dir_use_symlinks=False
)

print("Download complete")