# If not running interactively, don't do anything
case $- in
    *i*) ;;
      *) return;;
esac

# Don't put duplicate lines or lines starting with space in history
HISTCONTROL=ignoreboth

# Append to the history file instead of overwriting it
shopt -s histappend

# Set history length
HISTSIZE=1000
HISTFILESIZE=2000

# Update LINES and COLUMNS after each command
shopt -s checkwinsize

# Enable recursive globbing with ** pattern (optional)
#shopt -s globstar

# Set up color support for the prompt if available
case "$TERM" in
    xterm-color|*-256color) color_prompt=yes;;
esac

# Uncomment the line below to force color prompt
#force_color_prompt=yes

if [ -n "$force_color_prompt" ]; then
    if command -v tput &> /dev/null && tput setaf 1 &> /dev/null; then
        color_prompt=yes
    else
        color_prompt=
    fi
fi

# Set the prompt
if [ "$color_prompt" = yes ]; then
    PS1='\[\033[01;34m\]\w\[\033[00m\]\$ '
else
    PS1='\w\$ '
fi
unset color_prompt force_color_prompt

# Set terminal title for xterm
case "$TERM" in
    xterm*|rxvt*)
        PS1="\[\e]0;\w\a\]$PS1"
        ;;
esac

# Enable color support for ls
if command -v dircolors &> /dev/null; then
    test -r ~/.dircolors && eval "$(dircolors -b ~/.dircolors)" || eval "$(dircolors -b)"
    alias ls='ls --color=auto'
fi

# Load custom aliases if they exist
if [ -f ~/.bash_aliases ]; then
    . ~/.bash_aliases
fi

# Add ~/.local/bin to PATH if it exists
if [ -d "$HOME/.local/bin" ]; then
    PATH="$HOME/.local/bin:$PATH"
fi

# Enable bash completion if available
if ! shopt -oq posix; then
    if [ -f /usr/share/bash-completion/bash_completion ]; then
        . /usr/share/bash-completion/bash_completion
    elif [ -f /etc/bash_completion ]; then
        . /etc/bash_completion
    fi
fi
