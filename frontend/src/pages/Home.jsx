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
import { useNavigate } from "react-router-dom";

import api from "../api/axios";
import Image from "../component/Image";
import loadingGIF from "../assets/loading.gif";

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

  const navigate = useNavigate();

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
    if (gridArea == 0) setLeft(loadingGIF);
    else setRight(loadingGIF);
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
    let API = `/image-process/threshold/otsu`;
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
            setLeftMaxCluster(
              Array.from({ length: clusters }, (_, i) => i + 1)
            );
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
    if (side == 0) setLeft(loadingGIF);
    else setRight(loadingGIF);
    const API = "/image-process/segmentation/kmeanpp";
    api
      .get(API, {
        params: {
          imagePath: imagePath,
          nCluster: e.target.value,
        },
        responseType: "blob",
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
      .catch((err) => alert(`Lỗi: ${err.message}`));
  };

  return (
    <Stack
      gap={1}
      sx={{ width: "100vw", height: "100vh", alignItems: "center" }}
    >
      <Box
        sx={{
          display: "flex",
          width: "fit-content",
          flexDirection: "column",
          m: imagePath ? 3 : 50,
          // border: '1px solid black'
        }}
      >
        <Button
          component="label"
          role={undefined}
          variant="contained"
          tabIndex={-1}
          startIcon={<CloudUpload />}
          size={imagePath ? "medium" : "large"}
          sx={{ mb: 1 }}
        >
          Tải ảnh lên
          <VisuallyHiddenInput
            type="file"
            onChange={(e) => handleUploadImage(e)}
          />
        </Button>
        <Button variant="text" onClick={() => navigate("/beta")}>
          Try beta version
        </Button>
      </Box>

      {imagePath && (
        <Box>
          <Grid container width="100vw">
            <Grid
              size={6}
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
              gap={2}
            >
              <div>
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
              </div>
              <div style={{ background: "hsl(0, 0%, 90%)", width: "100%" }}>
                <Image src={left} />
              </div>
            </Grid>
            <Grid
              size={6}
              sx={{
                display: "flex",
                flexDirection: "column",
                alignItems: "center",
              }}
              gap={2}
            >
              <div>
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
              </div>
              <div style={{ background: "hsl(0, 0%, 90%)", width: "100%" }}>
                <Image src={right} />
              </div>
            </Grid>
          </Grid>
        </Box>
      )}
    </Stack>
  );
}
