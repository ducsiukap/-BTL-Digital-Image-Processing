import {
  Button,
  Stack,
  Divider,
  Box,
  Grid,
  Card,
  Select,
  MenuItem,
} from "@mui/material";
import { styled } from "@mui/material/styles";

import { CloudUpload } from "@mui/icons-material";
import { useState } from "react";

import api from "../api/axios";
import Image from "../component/Image";

const VisuallyHiddenInput = styled("input")({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
});

export default function Home() {
  const [leftOpts, setLeftOpts] = useState(1);
  const [rightOpts, setRightOpts] = useState(1);
  const [left, setLeft] = useState(null);
  const [right, setRight] = useState(null);
  const [leftCluster, setLeftCluster] = useState(2);
  const [rightCluster, setRightCluster] = useState(2);
  const [leftMaxCluster, setLeftMaxCluster] = useState();
  const [rightMaxCluster, setRightMaxCluster] = useState();

  const [original, setOriginal] = useState(null);
  const [imagePath, setImagePath] = useState(null);

  const handleUploadImage = (e) => {
    const image = e.target.files[0];
    if (!image) return;

    const formData = new FormData();
    formData.append("file", image);

    api
      .post("/image/upload", formData, {
        headers: {
          "Content-Type": "multipart/form-data",
        },
      })
      .then((res) => {
        setImagePath(res.data.imagePath);

        const imgURL = URL.createObjectURL(image);
        setOriginal(imgURL);
        setLeft(imgURL);
        setLeftOpts(1);
        setRight(imgURL);
        setRightOpts(1);
      })
      .catch((err) => alert(`Lỗi tải ảnh lên server: ${err.message}`));
  };

  const handleChangeSelect = (e, gridArea) => {
    if (e.target.value == 1) {
      if (gridArea == 0) {
        setLeftOpts(1);
        setLeft(original);
      } else {
        setRightOpts(1);
        setRight(original);
      }
      return;
    }

    // otsu
    let API = `/image-process/threshold-otsu`;
    // or kmean
    if (e.target.value === 3) API = "/image-process/segmentation/kmeanpp";

    api
      .get(API, {
        params: { imagePath: imagePath, nCluster: 2 },
        responseType: "blob",
      })
      .then((res) => {
        const imgURL = URL.createObjectURL(res.data);
        // console.log(res.headers)

        if (gridArea == 0) {
          setLeftOpts(e.target.value);
          setLeft(imgURL);
          if (e.target.value === 3) {
            setLeftCluster(2);
            const clusters = res.headers["x-max-cluster"];
            setLeftMaxCluster(Array.from({ length: clusters }, (_, i) => i));
          }
        } else {
          setRightOpts(e.target.value);
          setRight(imgURL);
          if (e.target.value === 3) {
            setRightCluster(2);
            const clusters = +res.headers["x-max-cluster"];
            setRightMaxCluster(
              Array.from({ length: clusters }, (_, i) => i + 1)
            );
          }
        }
      })
      .catch((err) => alert(`Lỗi: ${err.message}`));
  };

  const handleChangeCluster = (e, side) => {
    const API = "/image-process/segmentation/kmeanpp";
    api
      .get(API, {
        params: {
          imagePath: imagePath,
          nCluster: e.target.value,
        },
        responseType: 'blob',
      })
      .then((res) => {
        const imgURL = URL.createObjectURL(res.data);

        if (side === 0) {
          setLeftCluster(e.target.value);
          setLeft(imgURL);
        } else {
          setRightCluster(e.target.value);
          setRight(imgURL);
        }
      })
      .catch(err => alert(`Lỗi: ${err.message}`));
  };

  return (
    <Stack gap={2} sx={{ width: "100vw" }}>
      <Box sx={{ display: "flex", justifyContent: "center" }}>
        <Button
          component="label"
          role={undefined}
          variant="contained"
          tabIndex={-1}
          startIcon={<CloudUpload />}
          sx={{ width: "fit-content", m: imagePath ? 3 : 50 }}
          size={imagePath ? "medium" : "large"}
        >
          Tải ảnh lên
          <VisuallyHiddenInput
            type="file"
            onChange={(e) => handleUploadImage(e)}
          />
        </Button>
      </Box>

      {imagePath && <Divider />}

      {imagePath && (
        <Box>
          <Grid container>
            <Grid size={6}>
              <Select
                value={leftOpts}
                onChange={(e) => handleChangeSelect(e, 0)}
                sx={{ fontWeight: 600 }}
              >
                <MenuItem value={1} selected={true}>
                  Ảnh gốc
                </MenuItem>
                <MenuItem value={2}>Phân đoạn bằng phương áp Otsu</MenuItem>
                <MenuItem value={3}>Phân đoạn bằng Phân cụm K-means</MenuItem>
              </Select>
              {leftOpts === 3 && (
                <Select
                  value={leftCluster}
                  onChange={(e) => handleChangeCluster(e, 0)}
                  sx={{ fontWeight: 600 }}
                >
                  {leftMaxCluster.map((item) => (
                    <MenuItem value={item}>K = {item}</MenuItem>
                  ))}
                </Select>
              )}
              <br />
              <Image src={left} />
            </Grid>
            <Grid size={6}>
              <Select
                value={rightOpts}
                sx={{ fontWeight: 600 }}
                onChange={(e) => handleChangeSelect(e, 1)}
              >
                <MenuItem value={1} selected>
                  Ảnh gốc
                </MenuItem>
                <MenuItem value={2}>Phân đoạn bằng phương áp Otsu</MenuItem>
                <MenuItem value={3}>Phân đoạn bằng Phân cụm K-means</MenuItem>
              </Select>
              {rightOpts === 3 && (
                <Select
                  value={rightCluster}
                  onChange={(e) => handleChangeCluster(e, 1)}
                  sx={{ fontWeight: 600 }}
                >
                  {rightMaxCluster.map((item) => (
                    <MenuItem value={item}>K = {item}</MenuItem>
                  ))}
                </Select>
              )}
              <br />
              <Image src={right} />
            </Grid>
          </Grid>
        </Box>
      )}
    </Stack>
  );
}
