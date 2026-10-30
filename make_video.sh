#!/bin/bash
# ДАСТАН демо-видео жасау: Ken Burns zoom + fade
set -e
cd /home/shakan/til/screenshots

W=1440
H=900
DUR=4  # әр сурет секундта
FPS=30

# Desktop скриншоттар тәртібі
IMGS=(
  desktop_home.png
  desktop_dict.png
  desktop_gram.png
  desktop_read.png
  desktop_listen.png
  desktop_speak.png
  desktop_quiz.png
  desktop_prov.png
  desktop_jyr.png
  desktop_tongue.png
  desktop_food.png
  desktop_cloth.png
  desktop_legend.png
  desktop_history.png
  desktop_orn.png
  desktop_prog.png
)

# Mobile скриншоттар
MIMGS=(
  mobile_home.png
  mobile_dict.png
  mobile_quiz.png
  mobile_prov.png
  mobile_jyr.png
  mobile_speak.png
)

echo "=== Desktop видео жасау ==="

# Әр суретке zoom filter қолданып, жеке клип жасау
for i in "${!IMGS[@]}"; do
  F="${IMGS[$i]}"
  N=$((i+1))
  # Zoom: 1.0 -> 1.08 (баяу үлкейту)
  ffmpeg -y -loop 1 -i "$F" \
    -vf "scale=${W}:${H}:force_original_aspect_ratio=decrease,pad=${W}:${H}:(ow-iw)/2:(oh-ih)/2:black,\
zoompan=z='min(1+0.08*on/${DUR}/${FPS},1.08)':x='iw/2-(iw/zoom/2)':y='ih/2-(ih/zoom/2)':d=${DUR}*${FPS}:s=${W}x${H}:fps=${FPS},\
fade=t=in:st=0:d=0.5:color=white,fade=t=out:st=$((DUR-0.5)):d=0.5:color=white" \
    -c:v libx264 -pix_fmt yuv420p -preset fast -crf 23 \
    "/tmp/clip_$N.mp4" 2>/dev/null
  echo "  clip $N: $F"
done

# Барлық клипті біріктіру
echo "=== Клиптерді біріктіру ==="
LISTFILE=/tmp/filelist.txt
> $LISTFILE
for i in "${!IMGS[@]}"; do
  N=$((i+1))
  echo "file '/tmp/clip_$N.mp4'" >> $LISTFILE
done

ffmpeg -y -f concat -safe 0 -i $LISTFILE -c:v libx264 -pix_fmt yuv420p -preset medium -crf 22 \
  /home/shakan/til/dastan_demo.mp4 2>/dev/null

echo "=== Desktop видео дайын: dastan_demo.mp4 ==="
ls -lh /home/shakan/til/dastan_demo.mp4
