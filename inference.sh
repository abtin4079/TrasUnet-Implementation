#!/bin/bash

for i in {1..900}  # Using seq -w for zero-padded numbers
do
    image_path="/content/drive/MyDrive/kvasir/test/img/${i}.jpg"
    image_grad_path="/content/drive/MyDrive/kvasir/test/grad_img/${i}.png"

    # Check if the image file exists
    if [ -f "$image_path" ]; then
        python ./main.py --mode inference --model_path /content/drive/MyDrive/kvasir/model/model_adam_v1.pth --image_path "$image_path" --image_grad_path "$image_grad_path"
    else
        echo "File $image_path does not exist."
    fi
done
