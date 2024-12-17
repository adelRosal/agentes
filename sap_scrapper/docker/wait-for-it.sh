#!/bin/bash
# wait-for-it.sh: Espera a que un host/puerto esté disponible

WAITFORIT_cmdname=${0##*/}

echoerr() { if [[ $WAITFORIT_QUIET -ne 1 ]]; then echo "$@" 1>&2; fi }

usage()
{
    cat << USAGE >&2
Usage:
    $WAITFORIT_cmdname host:port [-s] [-t timeout] [-- command args]
    -h HOST | --host=HOST       Host o IP a testear
    -p PORT | --port=PORT       Puerto TCP a testear
    -s | --strict               Modo estricto
    -q | --quiet               No mostrar mensajes de error
    -t TIMEOUT | --timeout=TIMEOUT   Timeout en segundos, 0 para deshabilitar
    -- COMMAND ARGS             Ejecutar comando con args después del test
USAGE
    exit 1
}

wait_for()
{
    local wait_host=$1
    local wait_port=$2
    local timeout=$3
    local quiet=$4
    local strict=$5
    
    if [[ $timeout -gt 0 ]]; then
        echoerr "$WAITFORIT_cmdname: esperando $wait_host:$wait_port hasta $timeout segundos"
    else
        echoerr "$WAITFORIT_cmdname: esperando $wait_host:$wait_port sin timeout"
    fi
    
    start_ts=$(date +%s)
    while :
    do
        (echo > /dev/tcp/$wait_host/$wait_port) >/dev/null 2>&1
        result=$?
        if [[ $result -eq 0 ]]; then
            end_ts=$(date +%s)
            echoerr "$WAITFORIT_cmdname: $wait_host:$wait_port está disponible después de $((end_ts - start_ts)) segundos"
            break
        fi
        sleep 1
    done
    return $result
}

WAITFORIT_HOST=${1//:*/}
WAITFORIT_PORT=${1#*:}
shift
WAITFORIT_TIMEOUT=15
WAITFORIT_QUIET=0
WAITFORIT_STRICT=0
WAITFORIT_CHILD=0

# Procesar argumentos
while [[ $# -gt 0 ]]
do
    case "$1" in
        *:* )
        WAITFORIT_HOST=${1//:*/}
        WAITFORIT_PORT=${1#*:}
        shift 1
        ;;
        -q | --quiet)
        WAITFORIT_QUIET=1
        shift 1
        ;;
        -s | --strict)
        WAITFORIT_STRICT=1
        shift 1
        ;;
        -t)
        WAITFORIT_TIMEOUT="$2"
        if [[ $WAITFORIT_TIMEOUT == "" ]]; then break; fi
        shift 2
        ;;
        --timeout=*)
        WAITFORIT_TIMEOUT="${1#*=}"
        shift 1
        ;;
        --)
        shift
        WAITFORIT_CLI=("$@")
        break
        ;;
        --help)
        usage
        ;;
        *)
        echoerr "Unknown argument: $1"
        usage
        ;;
    esac
done

if [[ "$WAITFORIT_HOST" == "" || "$WAITFORIT_PORT" == "" ]]; then
    echoerr "Error: necesitas proporcionar un host y puerto para testear."
    usage
fi

wait_for "$WAITFORIT_HOST" "$WAITFORIT_PORT" "$WAITFORIT_TIMEOUT" "$WAITFORIT_QUIET" "$WAITFORIT_STRICT"
WAITFORIT_RESULT=$?

if [[ $WAITFORIT_CLI != "" ]]; then
    if [[ $WAITFORIT_RESULT -ne 0 && $WAITFORIT_STRICT -eq 1 ]]; then
        echoerr "$WAITFORIT_cmdname: modo estricto, rehusando ejecutar $WAITFORIT_CLI"
        exit $WAITFORIT_RESULT
    fi
    exec "${WAITFORIT_CLI[@]}"
else
    exit $WAITFORIT_RESULT
fi 