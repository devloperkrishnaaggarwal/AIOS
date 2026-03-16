# Nano Banana 2 API Documentation

> Generate content using the Nano Banana 2 model

## Overview

This document describes how to use the Nano Banana 2 model for content generation. The process consists of two steps:
1. Create a generation task
2. Query task status and results

## Authentication

All API requests require a Bearer Token in the request header:

```
Authorization: Bearer YOUR_API_KEY
```

Get API Key:
1. Visit [API Key Management Page](https://kie.ai/api-key) to get your API Key
2. Add to request header: `Authorization: Bearer YOUR_API_KEY`

---

## 1. Create Generation Task

### API Information
- **URL**: `POST https://api.kie.ai/api/v1/jobs/createTask`
- **Content-Type**: `application/json`

### Request Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| model | string | Yes | Model name: `nano-banana-2` |
| input | object | Yes | Input parameters object |
| callBackUrl | string | No | Callback URL for task completion notifications |

### input Object Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| prompt | string | Yes | Text description of the image (max 20000 chars) |
| image_input | array | No | Reference image URLs (up to 14, max 30MB each, jpeg/png/webp) |
| aspect_ratio | string | No | `1:1`, `1:4`, `1:8`, `2:3`, `3:2`, `3:4`, `4:1`, `4:3`, `4:5`, `5:4`, `8:1`, `9:16`, `16:9`, `21:9`, `auto` |
| google_search | boolean | No | Use Google Web Search grounding (default: false) |
| resolution | string | No | `1K`, `2K`, `4K` (default: `1K`) |
| output_format | string | No | `jpg` or `png` (default: `jpg`) |

### Request Example

```json
{
  "model": "nano-banana-2",
  "input": {
    "prompt": "A professional infographic about AI trends",
    "aspect_ratio": "9:16",
    "google_search": false,
    "resolution": "2K",
    "output_format": "png"
  }
}
```

### Response Example

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "281e5b0*********************f39b9"
  }
}
```

---

## 2. Query Task Status

### API Information
- **URL**: `GET https://api.kie.ai/api/v1/jobs/recordInfo`
- **Parameter**: `taskId` (URL query param)

### Response Example

```json
{
  "code": 200,
  "msg": "success",
  "data": {
    "taskId": "281e5b0*********************f39b9",
    "model": "nano-banana-2",
    "state": "success",
    "resultJson": "{\"resultUrls\":[\"https://...\"]}",
    "failCode": null,
    "failMsg": null,
    "costTime": 12500,
    "completeTime": 1757584176990,
    "createTime": 1757584164490
  }
}
```

### Task States

| State | Description |
|-------|-------------|
| `waiting` | Task is queued/processing |
| `success` | Task completed successfully |
| `fail` | Task failed |

---

## Error Codes

| Code | Description |
|------|-------------|
| 200 | Success |
| 400 | Invalid request parameters |
| 401 | Authentication failed |
| 402 | Insufficient balance |
| 404 | Resource not found |
| 422 | Parameter validation failed |
| 429 | Rate limit exceeded |
| 500 | Internal server error |
